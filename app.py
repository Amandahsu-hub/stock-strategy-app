
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📈 長榮短波策略模擬器（整合交易紀錄）")

# 讀取交易紀錄
df = pd.read_csv("trades.csv")
df["損益金額"] = (df["賣出價格"] - df["買進價格"]) * df["股數"]
df["報酬率"] = (df["賣出價格"] - df["買進價格"]) / df["買進價格"]

# 模擬邏輯設定
initial_capital = 100000
target_gain = 10000
stop_loss = -0.05
take_profit = 0.10

# 模擬策略結果
capital = initial_capital
results = []
months = df["交易月份"]
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

# 顯示表格
st.subheader("📋 模擬結果表")
st.dataframe(df_result)

# 統計資訊
st.subheader("📊 統計總結")
st.write(f"- 達標次數：{achieved} / {len(df)}")
st.write(f"- 達標率：{achieved / len(df):.0%}")
st.write(f"- 最長連續未達標：{max_streak} 個月")
if max_streak >= 3:
    st.error("⚠️ 建議檢討策略")
else:
    st.success("✅ 表現穩健")

# 繪圖
st.subheader("📈 資金成長曲線")
fig, ax = plt.subplots()
ax.plot(df_result["月份"], df_result["月末資金"], marker='o')
ax.axhline(initial_capital + target_gain, color='gray', linestyle='--', label='月目標線')
plt.xticks(rotation=45)
plt.title("資金成長趨勢")
plt.xlabel("月份")
plt.ylabel("資金總額")
plt.grid(True)
st.pyplot(fig)
