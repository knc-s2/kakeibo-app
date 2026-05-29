import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client

# -------------------------
# Supabase 設定
# -------------------------
SUPABASE_URL = "https://hoeaqaxjsjmwusvyevod.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhvZWFxYXhqc2ptd3Vzdnlldm9kIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk5OTg3NzksImV4cCI6MjA5NTU3NDc3OX0.BSMyfDv3IgSmE-cDAtDuyUhYegoMhQ2oqKHUNEuA4Ys"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# データ読み込み
# -------------------------
def load_data():
    response = supabase.table("kakeibo").select("*").order("id", desc=False).execute()
    if response.data:
        return pd.DataFrame(response.data)
    else:
        return pd.DataFrame(columns=[
            "id", "date", "year", "month", "record_type",
            "main_category", "sub_category", "person",
            "amount", "note"
        ])

df = load_data()

today = date.today()
this_year = today.year
this_month = today.month

st.set_page_config(page_title="家計簿アプリ", layout="wide")
st.title("家計簿アプリ")

# =========================
# マスタ定義（Streamlit版）
# =========================

variable_main_categories = [
    "食費", "雑費", "医療費", "勉強", "美容", "交際費", "趣味", "育児", "その他"
]

need_luxury_sub = ["必要", "贅沢"]
person_sub = ["だいき", "ななこ", "共通"]
medical_sub = ["だいき", "ななこ", "しゅうすけ", "共通"]

monthly_fixed_items = {
    "家賃": ["住宅ローン", "管理費・積立費", "駐車場"],
    "通信費": ["だいき携帯", "ななこ携帯"],
    "その他": ["電気代", "ガス代", "水道代"],
    "保険": ["だいき日生", "ななこ日生"],
    "コンタクト": ["だいきコンタクト", "ななこコンタクト"],
}

monthly_income_items = {
    "収入": ["だいきmain", "ななこmain", "だいき他", "ななこ他", "その他"]
}

annual_fixed_items = {
    "サブスク": ["AmazonPrime", "NintendoOnline"],
    "税金": ["自動車税", "固定資産税"],
    "その他": ["自動車保険"],
}

# =========================
# タブ
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["変動費入力", "月固定費・収入入力", "年固定費入力", "集計・グラフ", "データ削除"]
)

# -------------------------
# 変動費入力（UI 完全復元）
# -------------------------
with tab1:
    st.header("変動費の入力")

    col_date1, col_date2 = st.columns(2)
    with col_date1:
        input_date = st.date_input("日付", value=today)

    main_cat = st.selectbox("項目（変動費）", variable_main_categories)

    if main_cat in ["食費", "雑費", "育児", "その他"]:
        sub_cat = st.selectbox("サブ項目", need_luxury_sub)
        person = "共通"
    elif main_cat == "医療費":
        sub_cat = st.selectbox("サブ項目（誰の医療費か）", medical_sub)
        person = sub_cat
    else:
        sub_cat = st.selectbox("サブ項目（誰の支出か）", person_sub)
        person = sub_cat

    amount = st.number_input("金額", min_value=0, step=100)
    note = st.text_input("メモ（任意）")

    if st.button("この内容で登録", key="add_variable"):
        if amount > 0:
            new_row = {
                "date": input_date.isoformat(),
                "year": input_date.year,
                "month": input_date.month,
                "record_type": "variable",
                "main_category": main_cat,
                "sub_category": sub_cat,
                "person": person,
                "amount": amount,
                "note": note,
            }
            supabase.table("kakeibo").insert(new_row).execute()
            st.success("変動費を登録しました。")
        else:
            st.error("金額を入力してください。")

# -------------------------
# 月固定費・収入入力（UI 完全復元）
# -------------------------
with tab2:
    st.header("月固定費・収入の入力")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        target_year = st.number_input("対象年", min_value=2000, max_value=2100, value=this_year)
    with col_m2:
        target_month = st.number_input("対象月", min_value=1, max_value=12, value=this_month)

    st.subheader("月固定費の入力")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        fixed_main = st.selectbox("大カテゴリ（固定費）", list(monthly_fixed_items.keys()))
    with col_f2:
        fixed_sub = st.selectbox("項目", monthly_fixed_items[fixed_main])
    with col_f3:
        fixed_amount = st.number_input("金額（固定費）", min_value=0, step=100)

    fixed_note = st.text_input("メモ（固定費・任意）")

    if st.button("固定費を登録", key="add_monthly_fixed"):
        if fixed_amount > 0:
            new_row = {
                "date": date(target_year, target_month, 1).isoformat(),
                "year": target_year,
                "month": target_month,
                "record_type": "monthly_fixed",
                "main_category": fixed_main,
                "sub_category": fixed_sub,
                "person": "共通",
                "amount": fixed_amount,
                "note": fixed_note,
            }
            supabase.table("kakeibo").insert(new_row).execute()
            st.success("月固定費を登録しました。")
        else:
            st.error("金額を入力してください。")

    st.markdown("---")
    st.subheader("月収入の入力")

    col_i1, col_i2 = st.columns(2)
    with col_i1:
        income_main = "収入"
        income_sub = st.selectbox("収入項目", monthly_income_items[income_main])
    with col_i2:
        income_amount = st.number_input("金額（収入）", min_value=0, step=100)

    income_note = st.text_input("メモ（収入・任意）")

    if st.button("収入を登録", key="add_monthly_income"):
        if income_amount > 0:
            if "だいき" in income_sub:
                person = "だいき"
            elif "ななこ" in income_sub:
                person = "ななこ"
            else:
                person = "共通"

            new_row = {
                "date": date(target_year, target_month, 1).isoformat(),
                "year": target_year,
                "month": target_month,
                "record_type": "monthly_income",
                "main_category": income_main,
                "sub_category": income_sub,
                "person": person,
                "amount": income_amount,
                "note": income_note,
            }
            supabase.table("kakeibo").insert(new_row).execute()
            st.success("月収入を登録しました。")
        else:
            st.error("金額を入力してください。")

# -------------------------
# 年固定費入力（UI 完全復元）
# -------------------------
with tab3:
    st.header("年固定費の入力")

    target_year_annual = st.number_input(
        "対象年（年固定費）", min_value=2000, max_value=2100, value=this_year
    )

    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        annual_main = st.selectbox("大カテゴリ（年固定費）", list(annual_fixed_items.keys()))
    with col_a2:
        annual_sub = st.selectbox("項目（年固定費）", annual_fixed_items[annual_main])
    with col_a3:
        annual_amount = st.number_input("金額（年固定費）", min_value=0, step=100)

    annual_note = st.text_input("メモ（年固定費・任意）")

    if st.button("年固定費を登録", key="add_annual_fixed"):
        if annual_amount > 0:
            new_row = {
                "date": date(target_year_annual, 1, 1).isoformat(),
                "year": target_year_annual,
                "month": 0,
                "record_type": "annual_fixed",
                "main_category": annual_main,
                "sub_category": annual_sub,
                "person": "共通",
                "amount": annual_amount,
                "note": annual_note,
            }
            supabase.table("kakeibo").insert(new_row).execute()
            st.success("年固定費を登録しました。")
        else:
            st.error("金額を入力してください。")

# -------------------------
# 集計・グラフ（Streamlit版そのまま）
# -------------------------
with tab4:
    st.header("集計・グラフ")

    df = load_data()

    if df.empty:
        st.info("まだデータがありません。")
    else:
        df["year"] = df["year"].astype(int)
        df["month"] = df["month"].astype(int)
        df["amount"] = df["amount"].astype(float)

        st.subheader("月ごとの収支・貯蓄")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            view_year = st.number_input(
                "表示する年",
                min_value=int(df["year"].min()),
                max_value=int(df["year"].max()),
                value=this_year,
            )

        df_year = df[df["year"] == view_year].copy()

        def monthly_summary(df_year):
            income = df_year[df_year["record_type"] == "monthly_income"].groupby("month")["amount"].sum()
            fixed = df_year[df_year["record_type"] == "monthly_fixed"].groupby("month")["amount"].sum()
            variable = df_year[df_year["record_type"] == "variable"].groupby("month")["amount"].sum()
            annual = df_year[df_year["record_type"] == "annual_fixed"]["amount"].sum()

            months = range(1, 13)
            rows = []
            for m in months:
                inc = income.get(m, 0)
                fix = fixed.get(m, 0)
                var = variable.get(m, 0)
                total_expense = fix + var
                saving = inc - total_expense
                rows.append({
                    "month": m,
                    "income": inc,
                    "fixed_expense": fix,
                    "variable_expense": var,
                    "total_expense": total_expense,
                    "saving": saving,
                })
            return pd.DataFrame(rows), annual

        monthly_df, annual_fixed_total = monthly_summary(df_year)

        st.dataframe(monthly_df, use_container_width=True)
        st.bar_chart(
            monthly_df.set_index("month")[["income", "total_expense", "saving"]],
            use_container_width=True
        )

        st.markdown(f"**この年の年固定費合計：{annual_fixed_total:,.0f} 円**")

# -------------------------
# データ削除（Supabase対応）
# -------------------------
with tab5:
    st.header("データ削除")

    df = load_data()

    if df.empty:
        st.info("まだデータがありません。")
    else:
        st.dataframe(df)

        delete_id = st.number_input("削除したい id を入力", min_value=1, step=1)

        if st.button("この行を削除する"):
            supabase.table("kakeibo").delete().eq("id", delete_id).execute()
            st.success(f"id {delete_id} を削除しました！")
