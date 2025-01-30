import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 设置中文字体 - 使用系统自带的中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # MacOS 自带字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 读取CSV文件并打印列名
df = pd.read_csv('data.csv', encoding='utf-8')
print("CSV列名:", df.columns.tolist())

# 提取演员列表列
def extract_performers(row):
    if pd.isna(row):
        return []
    performers = str(row).split(' ')
    performers = [p.split('（')[0] for p in performers]
    return [p for p in performers if p]  # 移除空字符串

# 应用到performers列 - 使用正确的列名
df['performers_list'] = df['performers'].apply(extract_performers)  

# 创建图
G = nx.Graph()

# 遍历每个节目
for _, row in df.iterrows():
    performers = row['performers_list']
    year = row['year']  # 这个列名是正确的
    
    if not isinstance(performers, list) or len(performers) < 2:
        continue
        
    # 为同一个节目中的演员创建边
    for i in range(len(performers)):
        for j in range(i+1, len(performers)):
            p1, p2 = performers[i], performers[j]
            if not p1 or not p2:  # 跳过空值
                continue
            if G.has_edge(p1, p2):
                G[p1][p2]['weight'] += 1
                if year not in G[p1][p2]['years']:
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
print("\n最常合作的演员对:")
for p1, p2, data in top_collaborations[:10]:
    print(f"{p1}-{p2}: {data['weight']}次合作, 年份:{sorted(data['years'])}")

print("\n参与最多的演员:")
for name, centrality in top_performers[:10]:
    print(f"{name}: 中心度 {centrality:.3f}")

# 输出度中心度排名前10的演员
print("\n最有'人缘'的演员(度中心度):")
for name, centrality in sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]:
    # 计算直接合作演员数
    direct_collaborators = len([n for n in G.neighbors(name)])
    print(f"{name}: 度中心度 {centrality:.3f} (直接合作过 {direct_collaborators} 位演员)")

# 输出中介中心度排名前10的演员
print("\n最善于'牵线搭桥'的演员(中介中心度):")
for name, centrality in sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"{name}: 中介中心度 {centrality:.3f}")

# 分析演员的合作圈子
def get_collaboration_stats(name):
    """获取某个演员的合作统计信息"""
    if name not in G:
        return None
    
    collaborators = list(G.neighbors(name))
    total_collaborations = sum(G[name][c]['weight'] for c in collaborators)
    years = set()
    for c in collaborators:
        years.update(G[name][c]['years'])
    
    return {
        'collaborator_count': len(collaborators),
        'total_collaborations': total_collaborations,
        'active_years': sorted(years),
        'years_span': max(years) - min(years) if years else 0
    }

# 分析一些重要演员的合作情况
print("\n重要演员的合作统计:")
for name, _ in top_performers[:5]:
    stats = get_collaboration_stats(name)
    print(f"\n{name}:")
    print(f"- 合作过的演员数: {stats['collaborator_count']}")
    print(f"- 总合作次数: {stats['total_collaborations']}")
    print(f"- 活跃年份: {stats['active_years']}")
    print(f"- 跨越年份: {stats['years_span']}年")

try:
    # 绘制关系图
    pos = nx.spring_layout(G, k=2, iterations=100)  # 增加k值和迭代次数，使节点分布更开
    plt.figure(figsize=(30, 30))  # 增大图形尺寸

    # 只显示权重较大的边和重要节点
    min_weight = 3  # 增加最小权重阈值，减少边的数量
    significant_edges = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] >= min_weight]
    
    # 绘制边
    nx.draw_networkx_edges(G, pos, 
                          edgelist=significant_edges,
                          width=[G[u][v]['weight'] * 0.3 for (u, v) in significant_edges],
                          alpha=0.3,
                          edge_color='gray')
    
    # 绘制节点和标签
    top_nodes = [node for node, _ in top_performers[:50]]  # 增加显示的节点数量
    node_sizes = [degree_centrality[node] * 8000 for node in top_nodes]  # 增大节点尺寸
    
    nx.draw_networkx_nodes(G, pos, 
                          nodelist=top_nodes,
                          node_size=node_sizes,
                          node_color='lightblue',
                          alpha=0.6)
    
    # 只为重要节点添加标签
    labels = {node: node for node in top_nodes[:30]}  # 只显示前30个节点的标签
    nx.draw_networkx_labels(G, pos, 
                           labels,
                           font_size=10,
                           font_family='Arial Unicode MS')

    plt.title("春晚演员合作关系图谱 (重要节点)", fontproperties='Arial Unicode MS', fontsize=20)
    plt.axis('off')
    plt.savefig("relationship_graph.png", dpi=300, bbox_inches='tight')
    plt.close()
    
except Exception as e:
    print(f"绘图时出错: {str(e)}")

# 输出一些统计信息
print(f"\n总演员数: {len(G.nodes())}")
print(f"总合作关系数: {len(G.edges())}")
print(f"平均合作次数: {sum(nx.get_edge_attributes(G, 'weight').values()) / len(G.edges()):.2f}") 