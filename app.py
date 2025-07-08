
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="長榮短波策略模擬器", layout="centered")
st.title("📈 長榮短波策略模擬器（整合交易紀錄）")

CSV_FILE = "trades.csv"
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["交易月份", "股票代碼", "買進價格", "賣出價格", "股數"])
    df_init.to_csv(CSV_FILE, index=False)

with st.form("add_trade_form"):
    st.subheader("📝 輸入一筆新交易")
    col1, col2 = st.columns(2)
    month = col1.text_input("交易月份（格式：YYYY-MM）")
    symbol = col2.text_input("股票代碼（例如：2603）")
    col3, col4 = st.columns(2)
    buy_price = col3.number_input("買進價格", min_value=0.0, value=150.0)
    sell_price = col4.number_input("賣出價格", min_value=0.0, value=158.0)
    shares = st.number_input("股數", min_value=1, value=1000)
    submitted = st.form_submit_button("➕ 新增交易")
    if submitted and month and symbol:
        new_trade = pd.DataFrame([{
            "交易月份": month,
            "股票代碼": symbol,
            "買進價格": buy_price,
            "賣出價格": sell_price,
            "股數": shares
        }])
        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, new_trade], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success("✅ 成功新增交易紀錄！請重新整理以查看更新後結果。")

if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    if len(df) > 0:
        df["損益金額"] = (df["賣出價格"] - df["買進價格"]) * df["股數"]
        df["報酬率"] = (df["賣出價格"] - df["買進價格"]) / df["買進價格"]
        initial_capital = 100000
        target_gain = 10000
        stop_loss = -0.05
        take_profit = 0.10
        capital = initial_capital
        results = []
        streak = 0
        max_streak = 0
        achieved = 0
        for i, row in df.iterrows():
            r = row["報酬率"]
            note = ""
            if r <= stop_loss:
                r = stop_loss
                note = "⚠️ 停損"
            elif r >= take_profit:
                r = take_profit
                note = "✅ 停利"
            profit = capital * r
            capital += profit
            hit = profit >= target_gain
            if hit:
                streak = 0
            else:
                streak += 1
                max_streak = max(max_streak, streak)
            achieved += int(hit)
            results.append({
                "月份": row["交易月份"],
                "原始報酬率": f"{row['報酬率']:.2%}",
                "調整後報酬率": f"{r:.2%}",
                "當月損益": round(profit, 2),
                "月末資金": round(capital, 2),
                "備註": f"{note}｜{'✅ 達標' if hit else '❌ 未達標'}"
            })
        df_result = pd.DataFrame(results)
        st.subheader("📋 模擬結果表")
        st.dataframe(df_result)

        st.subheader("🗑️ 移除錯誤的交易紀錄")
        df_display = df.copy()
        df_display.index += 1
        st.dataframe(df_display)
        if len(df) > 0:
    remove_index = st.number_input("輸入要移除的交易編號（從上表第幾筆）", min_value=1, max_value=len(df), step=1)
    if st.button("刪除該筆交易紀錄"):
        df.drop(index=remove_index - 1, inplace=True)
        df.to_csv(CSV_FILE, index=False)
        st.success("✅ 已成功刪除，請重新整理查看最新紀錄")
            df.drop(index=remove_index - 1, inplace=True)
            df.to_csv(CSV_FILE, index=False)
            st.success("✅ 已成功刪除，請重新整理查看最新紀錄")

        st.subheader("📊 統計總結")
        st.write(f"- 達標次數：{achieved} / {len(df)}")
        if len(df) > 0:
        st.write(f"- 達標率：{achieved / len(df):.0%}")
    else:
        st.write("- 達標率：無法計算（無交易紀錄）")
        st.write(f"- 最長連續未達標：{max_streak} 個月")
        if max_streak >= 3:
            st.error("⚠️ 建議檢討策略")
        else:
            st.success("✅ 表現穩健")
        st.subheader("📈 資金成長曲線")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_result["月份"],
            y=df_result["月末資金"],
            mode='lines+markers',
            name='資金成長'
        ))
        fig.add_hline(y=initial_capital + target_gain, line_dash="dash", line_color="gray", annotation_text="月目標線")
        fig.update_layout(
            title="資金成長曲線",
            xaxis_title="月份",
            yaxis_title="資金總額",
        )
        st.plotly_chart(fig)

        st.subheader("📚 各股票總表紀錄")

        summary = df.copy()
        summary["損益金額"] = (summary["賣出價格"] - summary["買進價格"]) * summary["股數"]
        summary["總成本"] = summary["買進價格"] * summary["股數"]
        summary["總收益"] = summary["賣出價格"] * summary["股數"]
        group = summary.groupby("股票代碼").agg({
            "股數": "sum",
            "總成本": "sum",
            "總收益": "sum",
            "損益金額": "sum"
        }).rename(columns={
            "股數": "總股數",
            "總成本": "總成本",
            "總收益": "總收益",
            "損益金額": "總盈虧"
        })
        group["平均成本"] = group["總成本"] / group["總股數"]
        group["報酬率"] = (group["總收益"] - group["總成本"]) / group["總成本"]
        st.dataframe(group.reset_index())

    else:
        st.warning("尚未有交易紀錄，請先新增一筆！")
else:
    st.error("找不到交易紀錄檔案！")
