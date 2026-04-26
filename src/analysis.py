from pathlib import Path
from typing import Callable, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd

try:
	from .db import get_connection
except ImportError:
	# Allows running as a script: python src/analysis.py
	from db import get_connection


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "outputs"
CHARTS_DIR = OUTPUT_DIR / "charts"
TABLES_DIR = OUTPUT_DIR / "tables"


def run_sql(query: str) -> pd.DataFrame:
	"""Run a SQL query and return a DataFrame."""
	with get_connection() as conn:
		return pd.read_sql_query(query, conn)


def ensure_output_dirs() -> None:
	CHARTS_DIR.mkdir(parents=True, exist_ok=True)
	TABLES_DIR.mkdir(parents=True, exist_ok=True)


def save_table(df: pd.DataFrame, filename: str) -> None:
	df.to_csv(TABLES_DIR / filename, index=False)


def save_chart(filename: str) -> None:
	plt.tight_layout()
	plt.savefig(CHARTS_DIR / filename, dpi=150, bbox_inches="tight")
	plt.close()


def build_pareto(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
	"""Build sorted Pareto table with cumulative shares."""
	p = df[[group_col, value_col]].copy()
	p[value_col] = pd.to_numeric(p[value_col], errors="coerce")
	p = p.dropna(subset=[value_col])
	p = p.groupby(group_col, as_index=False)[value_col].sum()
	p = p.sort_values(value_col, ascending=False).reset_index(drop=True)
	p["rank"] = p.index + 1
	p["share_pct"] = 100.0 * p[value_col] / p[value_col].sum()
	p["cum_share_pct"] = p["share_pct"].cumsum()
	return p


def cutoff_rank(pareto_df: pd.DataFrame, threshold: float = 80.0) -> int:
	hit = pareto_df[pareto_df["cum_share_pct"] >= threshold]
	return int(hit.iloc[0]["rank"]) if not hit.empty else int(len(pareto_df))


def reorder_overview() -> None:
	reorder_split_df = run_sql(
		"""
		SELECT
		  CASE WHEN reordered = 1 THEN 'Reordered' ELSE 'First-time / Not Reordered' END AS reorder_type,
		  total_count
		FROM mv_reorder_rate
		ORDER BY reordered DESC
		"""
	)
	reorder_split_df["share_pct"] = 100.0 * reorder_split_df["total_count"] / reorder_split_df["total_count"].sum()
	save_table(reorder_split_df, "reorder_vs_non_reorder_split.csv")

	plt.figure(figsize=(6, 6))
	plt.pie(
		reorder_split_df["total_count"],
		labels=reorder_split_df["reorder_type"],
		autopct="%1.1f%%",
		startangle=90,
		wedgeprops={"linewidth": 1, "edgecolor": "white"},
	)
	plt.title("Reorder vs Non-Reorder Split")
	save_chart("01_reorder_vs_non_reorder_split.png")

	reorder_rate_hour_df = run_sql(
		"""
		SELECT
		  order_hour_of_day,
		  total_orders,
		  reorder_count,
		  ROUND(100.0 * reorder_rate, 2) AS reorder_rate_pct
		FROM mv_reorder_time_v2
		ORDER BY order_hour_of_day
		"""
	)
	save_table(reorder_rate_hour_df, "reorder_rate_by_hour.csv")

	plt.figure(figsize=(10, 4))
	plt.plot(reorder_rate_hour_df["order_hour_of_day"], reorder_rate_hour_df["reorder_rate_pct"], marker="o")
	plt.title("Reorder Rate by Hour")
	plt.xlabel("Hour of Day")
	plt.ylabel("Reorder Rate (%)")
	save_chart("02_reorder_rate_by_hour.png")

	top_reordered_products_df = run_sql(
		"""
		SELECT product_name, reorder_count, total_orders, reorder_rate
		FROM mv_reorder_product_v2
		ORDER BY reorder_count DESC
		LIMIT 15
		"""
	)
	save_table(top_reordered_products_df, "top_15_products_by_reorder_count.csv")

	plot_df = top_reordered_products_df.sort_values("reorder_count", ascending=True)
	plt.figure(figsize=(10, 6))
	plt.barh(plot_df["product_name"], plot_df["reorder_count"])
	plt.title("Top 15 Products by Reorder Count")
	plt.xlabel("Reorder Count")
	plt.ylabel("Product")
	save_chart("03_top_15_products_by_reorder_count.png")


def loyalty_and_action() -> None:
	product_loyalty_summary_df = run_sql(
		"""
		SELECT
			product_loyalty_band,
			COUNT(*) AS product_count,
			ROUND(AVG(reorder_rate_pct), 2) AS avg_reorder_rate_pct,
			SUM(total_orders) AS total_orders
		FROM (
			SELECT
				product_id,
				total_orders,
				ROUND(reorder_rate * 100, 2) AS reorder_rate_pct,
				CASE
					WHEN reorder_rate >= 0.75 AND total_orders >= 500 THEN 'Champion Product'
					WHEN reorder_rate >= 0.60 AND total_orders >= 200 THEN 'Loyal Product'
					WHEN reorder_rate >= 0.45 AND total_orders >= 100 THEN 'Potential Loyal Product'
					ELSE 'Low Loyalty Product'
				END AS product_loyalty_band
			FROM mv_reorder_product_v2
		) p
		GROUP BY product_loyalty_band
		ORDER BY product_count DESC
		"""
	)
	save_table(product_loyalty_summary_df, "product_loyalty_band_distribution.csv")

	plt.figure(figsize=(9, 4))
	plt.bar(product_loyalty_summary_df["product_loyalty_band"], product_loyalty_summary_df["product_count"])
	plt.title("Product Loyalty Band Distribution")
	plt.xlabel("Product Loyalty Band")
	plt.ylabel("Number of Products")
	plt.xticks(rotation=20)
	save_chart("04_product_loyalty_band_distribution.png")

	dept_loyalty_df = run_sql(
		"""
		SELECT
		  department,
		  total_orders,
		  reorder_count,
		  ROUND(100.0 * reorder_rate, 2) AS reorder_rate_pct
		FROM mv_reorder_department_v2
		ORDER BY reorder_rate DESC, total_orders DESC
		"""
	)
	save_table(dept_loyalty_df, "department_loyalty_comparison.csv")

	plot_dept = dept_loyalty_df.sort_values("reorder_rate_pct", ascending=True)
	plt.figure(figsize=(10, 6))
	plt.barh(plot_dept["department"], plot_dept["reorder_rate_pct"])
	plt.title("Department Loyalty Comparison")
	plt.xlabel("Reorder Rate (%)")
	plt.ylabel("Department")
	save_chart("05_department_loyalty_comparison.png")

	dept_action_df = run_sql(
		"""
		SELECT department, total_orders, reorder_rate
		FROM mv_reorder_department_v2
		"""
	)
	dept_action_df["order_share_pct"] = 100.0 * dept_action_df["total_orders"] / dept_action_df["total_orders"].sum()
	benchmark = dept_action_df["reorder_rate"].mean()
	dept_action_df["gap_to_benchmark"] = dept_action_df["reorder_rate"] - benchmark
	median_order_share = dept_action_df["order_share_pct"].median()

	def assign_action(row: pd.Series) -> str:
		high_volume = row["order_share_pct"] >= median_order_share
		low_loyalty = row["gap_to_benchmark"] < 0
		if high_volume and not low_loyalty:
			return "Defend"
		if high_volume and low_loyalty:
			return "Fix First"
		if (not high_volume) and not low_loyalty:
			return "Grow Selectively"
		return "Niche Monitor"

	dept_action_df["action_segment"] = dept_action_df.apply(assign_action, axis=1)
	save_table(dept_action_df, "department_action_matrix_data.csv")

	color_map = {
		"Defend": "#1f77b4",
		"Fix First": "#d62728",
		"Grow Selectively": "#2ca02c",
		"Niche Monitor": "#ff7f0e",
	}

	plt.figure(figsize=(10, 6))
	for segment, part in dept_action_df.groupby("action_segment"):
		plt.scatter(
			part["order_share_pct"],
			part["gap_to_benchmark"],
			s=80,
			alpha=0.85,
			label=segment,
			c=color_map.get(segment, "#7f7f7f"),
		)

	for _, row in dept_action_df.iterrows():
		plt.annotate(row["department"], (row["order_share_pct"], row["gap_to_benchmark"]), fontsize=8, alpha=0.9)

	plt.axvline(median_order_share, linestyle="--", linewidth=1)
	plt.axhline(0, linestyle="--", linewidth=1)
	plt.title("Department Action Matrix: Volume vs Loyalty Gap")
	plt.xlabel("Order Share (%)")
	plt.ylabel("Reorder Rate Gap vs Benchmark")
	plt.legend(title="Action Segment")
	save_chart("06_department_action_matrix_volume_vs_loyalty_gap.png")

	priority_df = (
		dept_action_df[dept_action_df["action_segment"] == "Fix First"]
		.sort_values(["order_share_pct", "gap_to_benchmark"], ascending=[False, True])
		[["department", "total_orders", "order_share_pct", "reorder_rate", "gap_to_benchmark", "action_segment"]]
		.reset_index(drop=True)
	)
	save_table(priority_df, "low_loyalty_high_volume_priorities.csv")


def basket_behavior() -> None:
	basket_df = run_sql("SELECT order_id, basket_size FROM mv_basket_analysis_v2")

	basket_summary_df = pd.DataFrame(
		{
			"metric": [
				"total_orders",
				"avg_basket_size",
				"median_basket_size",
				"p75_basket_size",
				"p90_basket_size",
				"max_basket_size",
			],
			"value": [
				int(basket_df["order_id"].nunique()),
				round(float(basket_df["basket_size"].mean()), 2),
				round(float(basket_df["basket_size"].median()), 2),
				round(float(basket_df["basket_size"].quantile(0.75)), 2),
				round(float(basket_df["basket_size"].quantile(0.90)), 2),
				int(basket_df["basket_size"].max()),
			],
		}
	)
	save_table(basket_summary_df, "basket_summary.csv")

	basket_dist_df = (
		basket_df.groupby("basket_size", as_index=False)
		.agg(order_count=("order_id", "count"))
		.sort_values("basket_size")
	)
	save_table(basket_dist_df, "basket_size_distribution.csv")

	plt.figure(figsize=(10, 4))
	plot_dist = basket_dist_df[basket_dist_df["basket_size"] <= basket_dist_df["basket_size"].quantile(0.95)]
	plt.plot(plot_dist["basket_size"], plot_dist["order_count"], marker="o")
	plt.title("Basket Size Distribution")
	plt.xlabel("Basket Size")
	plt.ylabel("Order Count")
	save_chart("07_basket_size_distribution.png")

	basket_segment_df = run_sql(
		"""
		WITH b AS (
			SELECT
				order_id,
				basket_size,
				CASE
					WHEN basket_size <= 5 THEN 'Small (1-5 items)'
					WHEN basket_size <= 15 THEN 'Medium (6-15 items)'
					ELSE 'Large (16+ items)'
				END AS basket_segment
			FROM mv_basket_analysis_v2
		)
		SELECT
			basket_segment,
			COUNT(*) AS order_count,
			ROUND(AVG(basket_size), 2) AS avg_basket_size,
			SUM(basket_size) AS total_items,
			ROUND(100.0 * COUNT(*)::numeric / SUM(COUNT(*)) OVER (), 2) AS order_share_pct,
			ROUND(100.0 * SUM(basket_size)::numeric / SUM(SUM(basket_size)) OVER (), 2) AS item_share_pct
		FROM b
		GROUP BY basket_segment
		ORDER BY avg_basket_size
		"""
	)
	save_table(basket_segment_df, "basket_segment_contribution.csv")

	fig, axes = plt.subplots(1, 2, figsize=(13, 4))

	axes[0].bar(basket_segment_df["basket_segment"], basket_segment_df["order_share_pct"])
	axes[0].set_title("Order Share by Basket Segment")
	axes[0].set_xlabel("Basket Segment")
	axes[0].set_ylabel("Order Share (%)")
	axes[0].tick_params(axis="x", rotation=15)

	axes[1].bar(basket_segment_df["basket_segment"], basket_segment_df["item_share_pct"])
	axes[1].set_title("Item Share by Basket Segment")
	axes[1].set_xlabel("Basket Segment")
	axes[1].set_ylabel("Item Share (%)")
	axes[1].tick_params(axis="x", rotation=15)

	save_chart("08_order_share_and_item_share_by_basket_segment.png")

	basket_pareto_df = run_sql(
		"""
		SELECT basket_size, COUNT(*) AS order_count
		FROM mv_basket_analysis_v2
		GROUP BY basket_size
		"""
	)
	basket_pareto_df = basket_pareto_df.sort_values("order_count", ascending=False).reset_index(drop=True)
	basket_pareto_df["rank"] = basket_pareto_df.index + 1
	basket_pareto_df["share_pct"] = 100.0 * basket_pareto_df["order_count"] / basket_pareto_df["order_count"].sum()
	basket_pareto_df["cum_share_pct"] = basket_pareto_df["share_pct"].cumsum()
	basket_cutoff = cutoff_rank(basket_pareto_df)
	save_table(basket_pareto_df, "basket_size_pareto.csv")

	plt.figure(figsize=(10, 4))
	plt.plot(basket_pareto_df["rank"], basket_pareto_df["cum_share_pct"], marker=".")
	plt.axhline(80, linestyle="--", linewidth=1)
	plt.axvline(basket_cutoff, linestyle=":", linewidth=1)
	plt.title("Basket Size Pareto Curve")
	plt.xlabel("Basket Size Rank")
	plt.ylabel("Cumulative Share of Orders (%)")
	save_chart("09_basket_size_pareto_curve.png")


def pareto_concentration() -> None:
	product_pareto = build_pareto(
		run_sql("SELECT product_name, total_orders FROM mv_product_performance_v2"),
		"product_name",
		"total_orders",
	)
	save_table(product_pareto, "product_pareto.csv")

	plt.figure(figsize=(10, 4))
	plt.plot(product_pareto["rank"], product_pareto["cum_share_pct"], marker=".")
	plt.axhline(80, linestyle="--")
	plt.title("Product Pareto Curve")
	plt.xlabel("Product Rank")
	plt.ylabel("Cumulative Share of Orders (%)")
	save_chart("10_product_pareto_curve.png")

	department_pareto = build_pareto(
		run_sql("SELECT department, total_orders FROM mv_department_performance_v2"),
		"department",
		"total_orders",
	)
	save_table(department_pareto, "department_pareto.csv")

	plt.figure(figsize=(8, 4))
	plt.plot(department_pareto["rank"], department_pareto["cum_share_pct"], marker="o")
	plt.axhline(80, linestyle="--")
	plt.title("Department Pareto Curve")
	plt.xlabel("Department Rank")
	plt.ylabel("Cumulative Share of Orders (%)")
	save_chart("11_department_pareto_curve.png")

	hour_pareto = build_pareto(
		run_sql("SELECT order_hour_of_day, total_orders FROM mv_orders_time_v2"),
		"order_hour_of_day",
		"total_orders",
	)
	save_table(hour_pareto, "order_hour_pareto.csv")

	plt.figure(figsize=(8, 4))
	plt.plot(hour_pareto["rank"], hour_pareto["cum_share_pct"], marker="o")
	plt.axhline(80, linestyle="--")
	plt.title("Order Hour Pareto Curve")
	plt.xlabel("Hour Rank")
	plt.ylabel("Cumulative Share of Orders (%)")
	save_chart("12_order_hour_pareto_curve.png")

	basket_pareto = run_sql(
		"""
		SELECT basket_size, COUNT(*) AS order_count
		FROM mv_basket_analysis_v2
		GROUP BY basket_size
		"""
	)
	basket_pareto = basket_pareto.sort_values("order_count", ascending=False).reset_index(drop=True)
	basket_pareto["rank"] = basket_pareto.index + 1
	basket_pareto["share_pct"] = 100.0 * basket_pareto["order_count"] / basket_pareto["order_count"].sum()
	basket_pareto["cum_share_pct"] = basket_pareto["share_pct"].cumsum()

	cutoff_compare_df = pd.DataFrame(
		{
			"dimension": ["Products", "Departments", "Order Hours", "Basket Sizes"],
			"groups_needed_for_80pct": [
				cutoff_rank(product_pareto),
				cutoff_rank(department_pareto),
				cutoff_rank(hour_pareto),
				cutoff_rank(basket_pareto),
			],
			"total_groups": [
				int(len(product_pareto)),
				int(len(department_pareto)),
				int(len(hour_pareto)),
				int(len(basket_pareto)),
			],
		}
	)
	cutoff_compare_df["pct_groups_needed"] = (
		100.0 * cutoff_compare_df["groups_needed_for_80pct"] / cutoff_compare_df["total_groups"]
	)
	save_table(cutoff_compare_df, "pareto_80_cutoff_comparison.csv")

	plt.figure(figsize=(9, 4))
	plt.bar(cutoff_compare_df["dimension"], cutoff_compare_df["pct_groups_needed"])
	plt.title("80% Cutoff Comparison")
	plt.ylabel("% of Groups Needed")
	plt.xlabel("Dimension")
	save_chart("13_80pct_cutoff_comparison.png")


def run_pipeline(steps: List[Tuple[str, Callable[[], None]]]) -> None:
	for step_name, step_fn in steps:
		print(f"Running: {step_name}")
		step_fn()
		print(f"Done: {step_name}\n")


def main() -> None:
	ensure_output_dirs()
	steps = [
		("Reorder Overview", reorder_overview),
		("Loyalty and Department Action", loyalty_and_action),
		("Basket Behavior", basket_behavior),
		("Pareto Concentration", pareto_concentration),
	]

	run_pipeline(steps)

	print("All analysis completed.")
	print(f"Charts saved to: {CHARTS_DIR}")
	print(f"Tables saved to: {TABLES_DIR}")


if __name__ == "__main__":
	main()