# -*- coding:utf-8 -*-
import sys
import pandas as pd
from WindClient import *
import time
import datetime
import os

reload(sys)
sys.setdefaultencoding('utf-8')


from PyQt4.QtGui import *
from PyQt4.QtCore import *
class main_view(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle(u'!!')
        self.window = QWidget()
        self.main_Layout = QHBoxLayout()
        self.update = QPushButton(u'更新')
        self.main_Layout.addWidget(self.update)
        self.setLayout(self.main_Layout)
        self.resize(150, 100)
        self.strategy_files, self.strategies, self.strategy_stocks_list = self.read_strategt()
        self.time_out()

        self.time = QTimer()
        self.time.start(5000)
        self.window.connect(self.time, SIGNAL('timeout()'), self.time_out)
        self.window.connect(self.update, SIGNAL('clicked()'), self.click_update)

        # print chg_dataframe

    # 读取需要的文件，输出策略数据
    def read_strategt(self):
        strategy_dir = os.path.join(os.getcwd(),'strategy')
        strategy_files = os.listdir(strategy_dir)
        print strategy_files
        strategies = []
        for strategy in strategy_files:
            if strategy.decode('gbk') == 'Thumbs.db':
                continue
            strategies.append(pd.read_excel(os.path.join(strategy_dir, strategy)).set_index(['stock']))
        strategy_stocks_list = []
        for num in range(len(strategies)):
            strategy_stocks_list = strategy_stocks_list + strategies[num].index.tolist()
        set_strategy_stocks_list = list(set(strategy_stocks_list))
        return strategy_files, strategies, set_strategy_stocks_list

    # 拿指数价格
    def get_index_chg(self):
        chg = w.wsq(['000905.SH', '000300.SH'], 'rt_pct_chg')
        ic_chg = chg.Data[0][0]
        if_chg = chg.Data[0][1]
        return ic_chg, if_chg

    # 拿股票价格
    def get_stocks_chg(self, stocks_list):
        chg = w.wsq(stocks_list, 'rt_pct_chg')
        chg_df = pd.DataFrame({'chg': chg.Data[0]}, index=chg.Codes)
        return chg_df

    # 显示
    def display(self, strategy_files, strategies, strategy_stocks_list):
        # 拿实时数据
        start_time = datetime.datetime.now()
        IC, IF = self.get_index_chg()
        chg_dataframe = self.get_stocks_chg(strategy_stocks_list)
        end_time = datetime.datetime.now()
        print u'获取数据时间:', (end_time - start_time).total_seconds()*1000,u'毫秒'
        # 算出策略BP
        for num in range(len(strategies)):
            chg_dataframe.index.name = 'stock'
            # print strategies[num].sort_index() , chg_dataframe.sort_index()
            # print len(strategies[num]) ,len(chg_dataframe)
            strategies[num] = strategies[num].sort_index()
            chg_dataframe = chg_dataframe.sort_index()
            strategies[num]['chg'] = chg_dataframe['chg']
            strategies[num]['wei_chg'] = strategies[num]['chg'] * strategies[num]['weight']*100
            print strategy_files[num].split('.')[0], (16-len(strategy_files[num].split('.')[0]))*' ',\
                round(strategies[num]['wei_chg'].sum()-IC*10000, 2), (8-len(str(round(strategies[num]['wei_chg'].sum()-IC*10000, 2))))*' ',\
                round(strategies[num]['wei_chg'].sum()-IF*10000, 2), (9-len(str(round(strategies[num]['wei_chg'].sum()-IF*10000, 2))))*' ',\
                round(strategies[num]['wei_chg'].sum(), 2)\


    def time_out(self):
        self.display(self.strategy_files, self.strategies, self.strategy_stocks_list)

    def click_update(self):
        self.strategy_files, self.strategies, self.strategy_stocks_list = self.read_strategt()
        self.time_out()


if __name__ == '__main__':
    w.start()
    app = QApplication(sys.argv)
    main_view = main_view()
    main_view.show()
    app.exec_()
