from pyecharts.charts import Pie, Bar, Scatter, Radar, HeatMap, Funnel, WordCloud
from pyecharts import options as opts
from pyecharts.globals import SymbolType
import pandas as pd

def create_pie_chart(data, title="", height="400px", show_top=None):
    pie = Pie(init_opts=opts.InitOpts(height=height, width="100%"))
    if show_top and len(data) > show_top:
        top_data = data.head(show_top)
        other_sum = data.iloc[show_top:].sum()
        pie_data = list(zip(top_data.index.tolist(), top_data.values.tolist()))
        if other_sum > 0:
            pie_data.append(('其他', other_sum))
    else:
        pie_data = [list(z) for z in zip(data.index.tolist(), data.values.tolist())]
    pie.add(
        "",
        pie_data,
        radius=["30%", "55%"],
        center=["40%", "50%"],
        label_opts=opts.LabelOpts(formatter="{b}: {d}%", font_size=10)
    )
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title=title),
        legend_opts=opts.LegendOpts(
            orient="vertical", 
            pos_top="middle", 
            pos_left="70%",
            item_width=10, 
            item_height=10, 
            textstyle_opts=opts.TextStyleOpts(font_size=9)
        )
    )
    return pie

def create_bar_chart(x_data, y_data, title="", x_name="", y_name="", height="400px", horizontal=False):
    bar = Bar(init_opts=opts.InitOpts(height=height))
    if horizontal:
        bar.add_xaxis(y_data)
        bar.add_yaxis("", x_data, label_opts=opts.LabelOpts(position="right"))
        bar.reversal_axis()
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(name=x_name),
            yaxis_opts=opts.AxisOpts(name=y_name, axislabel_opts=opts.LabelOpts(font_size=10))
        )
    else:
        bar.add_xaxis(x_data)
        bar.add_yaxis("", y_data)
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(name=x_name, axislabel_opts=opts.LabelOpts(rotate=45, font_size=10)),
            yaxis_opts=opts.AxisOpts(name=y_name)
        )
    return bar

def create_scatter_chart(x_data, y_data, size_data=None, title="", x_name="", y_name="", height="400px"):
    scatter = Scatter(init_opts=opts.InitOpts(height=height))
    scatter.add_xaxis(x_data)
    scatter.add_yaxis(
        "",
        y_data,
        symbol_size=lambda data: size_data[data[0]] if size_data is not None else 10,
        label_opts=opts.LabelOpts(is_show=False)
    )
    scatter.set_global_opts(
        title_opts=opts.TitleOpts(title=title),
        xaxis_opts=opts.AxisOpts(name=x_name),
        yaxis_opts=opts.AxisOpts(name=y_name),
        visualmap_opts=opts.VisualMapOpts(is_show=False) if size_data is None else None
    )
    return scatter

def create_radar_chart(indicators, values, title="", height="400px"):
    radar = Radar(init_opts=opts.InitOpts(height=height))
    radar.add_schema(schema=[opts.RadarIndicatorItem(name=k, max_=v) for k, v in indicators.items()])
    radar.add("", values, areastyle_opts=opts.AreaStyleOpts(opacity=0.3))
    radar.set_global_opts(title_opts=opts.TitleOpts(title=title))
    return radar

def create_heatmap_chart(x_data, y_data, value_data, title="", height="400px"):
    heatmap = HeatMap(init_opts=opts.InitOpts(height=height))
    data = []
    for i, x in enumerate(x_data):
        for j, y in enumerate(y_data):
            if i < len(value_data) and j < len(value_data[i]):
                data.append([i, j, value_data[i][j]])
    heatmap.add_xaxis(x_data)
    heatmap.add_yaxis("", y_data, data)
    heatmap.set_global_opts(
        title_opts=opts.TitleOpts(title=title),
        visualmap_opts=opts.VisualMapOpts(is_show=True, min_=0, max_=max([v for row in value_data for v in row if v]) if value_data else 100)
    )
    return heatmap

def create_wordcloud(words_data, title="", height="400px"):
    wordcloud = WordCloud(init_opts=opts.InitOpts(height=height))
    wordcloud.add("", words_data, word_size_range=[12, 60])
    wordcloud.set_global_opts(title_opts=opts.TitleOpts(title=title))
    return wordcloud

def create_funnel_chart(data, title="", height="400px"):
    funnel = Funnel(init_opts=opts.InitOpts(height=height))
    funnel.add("", [list(z) for z in zip(data.index.tolist(), data.values.tolist())])
    funnel.set_global_opts(title_opts=opts.TitleOpts(title=title))
    return funnel