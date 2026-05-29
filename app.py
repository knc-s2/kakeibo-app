import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client

# -------------------------
# Supabase 設定(FamMiwa3031)
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

# -------------------------
# Streamlit UI
# -------------------------
st.title("家計簿アプリ（Supabase版）")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["変動費入力", "月固定費・収入入力", "年固定費入力", "集計・グラフ", "データ削除"]
)

# -------------------------
# 変動費入力
# -------------------------
with tab1:
    st.header("変動費入力")

    input_date = st.date_input("日付", date.today(), key="date_variable")
    main_cat = st.selectbox("大カテゴリ", ["食費", "日用品", "娯楽", "交通", "その他"])
    sub_cat = st.text_input("サブカテゴリ", key="sub_variable")
    person = st.selectbox("誰の支出？", ["共通", "だいき", "ななこ"], key="person_variable")
    amount = st.number_input("金額", min_value=0, key="amount_variable")
    note = st.text_input("メモ", key="note_variable")

    if st.button("登録する"):
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
        st.success("変動費を登録しました！")

# -------------------------
# 月固定費・収入入力
# -------------------------
with tab2:
    st.header("月固定費・収入入力")

    input_date = st.date_input("日付", date.today(), key="date_monthly")
    record_type = st.selectbox("種類", ["monthly_fixed", "monthly_income"])
    main_cat = st.text_input("大カテゴリ", key="main_monthly")
    sub_cat = st.text_input("サブカテゴリ", key="sub_monthly")
    person = st.selectbox("誰の支出？", ["共通", "だいき", "ななこ"], key="person_person_monthly")
    amount = st.number_input("金額", min_value=0, key="amount_monthly")
    note = st.text_input("メモ", key="note_monthly")

    if st.button("登録する", key="monthly"):
        new_row = {
            "date": input_date.isoformat(),
            "year": input_date.year,
            "month": input_date.month,
            "record_type": record_type,
            "main_category": main_cat,
            "sub_category": sub_cat,
            "person": person,
            "amount": amount,
            "note": note,
        }
        supabase.table("kakeibo").insert(new_row).execute()
        st.success("月固定費/収入を登録しました！")

# -------------------------
# 年固定費入力
# -------------------------
with tab3:
    st.header("年固定費入力")

    input_date = st.date_input("日付", date.today(), key="date_annual")
    main_cat = st.text_input("大カテゴリ", key="main_annual")
    sub_cat = st.text_input("サブカテゴリ", key="sub_annual")
    person = st.selectbox("誰？", ["共通", "だいき", "ななこ"], key="person_annual")
    amount = st.number_input("金額", min_value=0, key="amount_annual")
    note = st.text_input("メモ", key="note_annual")

    if st.button("登録する", key="annual"):
        new_row = {
            "date": input_date.isoformat(),
            "year": input_date.year,
            "month": input_date.month,
            "record_type": "annual_fixed",
            "main_category": main_cat,
            "sub_category": sub_cat,
            "person": person,
            "amount": amount,
            "note": note,
        }
        supabase.table("kakeibo").insert(new_row).execute()
        st.success("年固定費を登録しました！")

# -------------------------
# 集計・グラフ
# -------------------------
with tab4:
    st.header("集計")

    df = load_data()
    st.dataframe(df)

    if not df.empty:
        monthly_sum = df.groupby(["year", "month"])["amount"].sum().reset_index()
        st.subheader("月ごとの合計")
        st.dataframe(monthly_sum)

# -------------------------
# データ削除
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
