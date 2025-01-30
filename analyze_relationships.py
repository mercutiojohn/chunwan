import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']

# 读取CSV文件
df = pd.read_csv('data.csv', encoding='utf-8')

# 提取演员列表列
def extract_performers(row):
    if pd.isna(row):
        return []
    performers = row.split(' ')
    performers = [p.split('（')[0] for p in performers]
    return performers

# 应用到performers列
df['performers_list'] = df['performers'].apply(extract_performers)

# 创建图
G = nx.Graph()

# 遍历每个节目
for _, row in df.iterrows():
    performers = row['performers_list']
    year = row['year']
    
    # 为同一个节目中的演员创建边
    for i in range(len(performers)):
        for j in range(i+1, len(performers)):
            p1, p2 = performers[i], performers[j]
            if G.has_edge(p1, p2):
                G[p1][p2]['weight'] += 1
                G[p1][p2]['years'].append(year)
            else:
                G.add_edge(p1, p2, weight=1, years=[year])

# 计算中心度
degree_centrality = nx.degree_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G)

# 找出最常合作的演员对
top_collaborations = sorted(G.edges(data=True), 
                          key=lambda x: x[2]['weight'],
                          reverse=True)

# 找出参与最多的演员
top_performers = sorted(degree_centrality.items(),
                      key=lambda x: x[1],
                      reverse=True)

# 输出分析结果
print("最常合作的演员对:")
for p1, p2, data in top_collaborations[:10]:
    print(f"{p1}-{p2}: {data['weight']}次合作, 年份:{data['years']}")

print("\n参与最多的演员:")
for name, centrality in top_performers[:10]:
    print(f"{name}: 中心度 {centrality:.3f}")

# 绘制关系图
pos = nx.spring_layout(G)
plt.figure(figsize=(15, 15))

node_size = [v * 3000 for v in degree_centrality.values()]
edge_width = [d['weight'] * 0.5 for (u, v, d) in G.edges(data=True)]

nx.draw(G, pos,
        node_size=node_size,
        width=edge_width,
        with_labels=True,
        font_size=8)

plt.title("春晚演员合作关系图谱")
plt.savefig("relationship_graph.png") 