#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore,QtWidgets
import ui_autosync
import os
import sys
import os.path
import string
import getpass
import shutil


class Auto_Sync(QtCore.QThread):
    sync_signal=QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self,parent)
        self.mode=None
        self.running=False
        self.workingDirectory=None
        self.mirrorDirectory=None
    def run(self):
        if self.mode=='mirror':
            while self.running:
                self.sync_action(self.workingDirectory,self.mirrorDirectory)
        elif self.mode=='copy':
            self.copy_action(self.workingDirectory,self.mirrorDirectory)
    def sync_action(self, path_A, path_B):
        try:
            set1=set(os.listdir(path_A))
            set2=set(os.listdir(path_B))

            d_temp1=set1-set2
            d_temp2=set2-set1
            d_temp3=set1&set2
            for file in d_temp1:
                lock_files=('.goutputstream','.~lock.','.swp','.{0}.swp'.format(file))
                if os.path.isfile(os.path.join(path_A,file)) and os.path.getsize(os.path.join(path_A,file))>0 and not( file.endswith(lock_files) or file.startswith(lock_files)):
                    shutil.copy(os.path.join(path_A,file),os.path.join(path_B,file))
                    self.sync_signal.emit('{0} -> {1}'.format(os.path.join(path_A,file),os.path.join(path_B,file)))
                if os.path.isdir(os.path.join(path_A,file)):
                    shutil.copytree(os.path.join(path_A,file),os.path.join(path_B,file))
                    self.sync_signal.emit('{0} -> {1}'.format(os.path.join(path_A,file),os.path.join(path_B,file)))

            for file in d_temp2:
                if os.path.isfile(os.path.join(path_B,file)):
                    os.remove(os.path.join(path_B,file))
                    self.sync_signal.emit('удален {0}'.format(os.path.join(path_B,file)))
                if os.path.isdir(os.path.join(path_B,file)):
                    shutil.rmtree(os.path.join(path_B,file),ignore_errors=True)
                    self.sync_signal.emit('удален {0}'.format(os.path.join(path_B,file)))

            for file in d_temp3:
                if os.path.isfile(os.path.join(path_A,file)):
                    if os.path.getmtime(os.path.join(path_A,file))>os.path.getmtime(os.path.join(path_B,file)):
                        shutil.copy(os.path.join(path_A,file),os.path.join(path_B,file))
                        os.utime(os.path.join(path_B,file), (os.path.getatime(os.path.join(path_A,file)),os.path.getmtime(os.path.join(path_A,file))))
                        self.sync_signal.emit('{0} -> {1}'.format(os.path.join(path_A,file),os.path.join(path_B,file)))
                    else:
                        pass

       #рекурсивный вызов ф-ии для проверки директории
                elif os.path.isdir(os.path.join(path_A,file)):
                    self.sync_action(os.path.join(path_A,file),os.path.join(path_B,file))
        except Exception as err:
            with open('sync_log.txt', 'a') as log:
                log.write(str(err)+'\n')
                self.sync_signal.emit('!!!Ошибка!!! \n {}'.format(err))
                self.running=False

    def copy_action(self, path_A, path_B):
        try:
            set1=set(os.listdir(path_A))
            set2=set(os.listdir(path_B))

            d_temp1=set1-set2
            d_temp3=set1&set2
            for file in d_temp1:
                lock_files=('.goutputstream','.~lock.','.swp','.{0}.swp'.format(file))
                if os.path.isfile(os.path.join(path_A,file)) and os.path.getsize(os.path.join(path_A,file))>0 and not( file.endswith(lock_files) or file.startswith(lock_files)):
                    shutil.copy(os.path.join(path_A,file),os.path.join(path_B,file))
                    self.sync_signal.emit('{0} -> {1}'.format(os.path.join(path_A,file),os.path.join(path_B,file)))
                if os.path.isdir(os.path.join(path_A,file)):
                    shutil.copytree(os.path.join(path_A,file),os.path.join(path_B,file))
                    self.sync_signal.emit('{0} -> {1}'.format(os.path.join(path_A,file),os.path.join(path_B,file)))

            for file in d_temp3:
                if os.path.isfile(os.path.join(path_A,file)):
                    if os.path.getmtime(os.path.join(path_A,file))>os.path.getmtime(os.path.join(path_B,file)):
                        shutil.copy(os.path.join(path_A,file),os.path.join(path_B,file))
                        os.utime(os.path.join(path_B,file), (os.path.getatime(os.path.join(path_A,file)),os.path.getmtime(os.path.join(path_A,file))))
                        self.sync_signal.emit('{0} -> {1}'.format(os.path.join(path_A,file),os.path.join(path_B,file)))
                    else:
                        pass

       #рекурсивный вызов ф-ии для проверки директории
                elif os.path.isdir(os.path.join(path_A,file)):
                    self.sync_action(os.path.join(path_A,file),os.path.join(path_B,file))
            self.sync_signal.emit('Копирование завершено.')
        except Exception as err:
            with open('sync_log.txt', 'a') as log:
                log.write(str(err)+'\n')
                self.sync_signal.emit('!!!Ошибка!!! \n {}'.format(err))
                self.running=False

          
           

class MyWindow(QtWidgets.QWidget, ui_autosync.Ui_Form):
    def __init__(self,parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.setupUi(self)
        self.dir_name=None
        self.combo_list=['']
        self.comboBox_work.activated[str].connect(self.work_dir)
        self.comboBox_mirror.activated[str].connect(self.mirror_dir)
        self.lineEdit.textChanged[str].connect(self.linetext)
        self.OkBtn.clicked.connect(self.ok_handler)
        self.StartBtn.clicked.connect(self.start_handler)
        self.radioCopy.clicked.connect(self.rdcopy)
        self.radioMirror.clicked.connect(self.rdmirr)
        self.ResetBtn.clicked.connect(self.reset_handler)
        self.StopBtn.clicked.connect(self.stop_handler)
        self.btnQuit.clicked.connect(QtWidgets.qApp.quit)
        self.ResetBtn.setDisabled(False)
        self.StopBtn.setDisabled(True)
        self.auto_sync=Auto_Sync()
        self.auto_sync.sync_signal.connect(self.sync_text, QtCore.Qt.QueuedConnection)
        self.init_os()
    def init_os(self):
        if os.name=='posix':
            self.os_name='Linux'
        elif os.name=='nt':
            self.os_name='Windows'
        self.textEdit.append('Определена ОС: {}'.format(self.os_name))
        self.textEdit.append('Введите имя директории для синхронизации и нажмите кнопку "Ok".')
    def rdcopy(self):
        self.auto_sync.mode='copy'
    def rdmirr(self):
        self.auto_sync.mode='mirror'
    def linetext(self,text):
        self.dir_name=text
    def sync_text(self,text):
        self.textEdit.append(text)
        if text=='Копирование завершено.':
            self.stop_handler()
    def ok_handler(self):
        if self.dir_name:  
            self.OkBtn.setDisabled(True)
            self.ResetBtn.setDisabled(False)
            self.launcher()
        else:
            self.textEdit.append('!!!Не определены необходимые параметры!!!')
    def reset_handler(self):
        self.radioCopy.setDisabled(False)
        self.radioMirror.setDisabled(False)
        self.auto_sync.workingDirectory=None
        self.auto_sync.mirrorDirectory=None
        self.OkBtn.setDisabled(False)
        self.dir_name=None
        self.combo_list=['']
        self.comboBox_work.clear()
        self.comboBox_mirror.clear()
        self.lineEdit.clear()
    def start_handler(self):
        if self.auto_sync.workingDirectory and self.auto_sync.mirrorDirectory and self.dir_name and self.auto_sync.mode:
            if self.auto_sync.workingDirectory==self.auto_sync.mirrorDirectory:
                self.textEdit.append('Рабочая директория и директория-зеркало не могут совпадать!')
            else:
                if self.auto_sync.mode=='copy':
                    self.radioMirror.setDisabled(True)
                elif self.auto_sync.mode=='mirror':
                    self.radioCopy.setDisabled(True)
                self.ResetBtn.setDisabled(True)
                self.StartBtn.setDisabled(True)
                self.comboBox_work.setDisabled(True)
                self.comboBox_mirror.setDisabled(True)
                self.StopBtn.setDisabled(False)
                self.auto_sync.running=True
                self.auto_sync.start()
        else:
            self.textEdit.append('!!!Не определены необходимые параметры!!!')
    def stop_handler(self):
        self.radioMirror.setDisabled(False)
        self.radioCopy.setDisabled(False)
        self.auto_sync.running=False
        self.comboBox_work.setDisabled(False)
        self.comboBox_mirror.setDisabled(False)
        self.StartBtn.setDisabled(False)
        self.ResetBtn.setDisabled(False)
        self.OkBtn.setDisabled(False)
        self.auto_sync.workingDirectory=None
        self.auto_sync.mirrorDirectory=None
        self.dir_name=None
        self.StopBtn.setDisabled(True)
        self.combo_list=['']
        self.comboBox_work.clear()
        self.comboBox_mirror.clear()
        self.lineEdit.clear()
        self.textEdit.append('!!!!Процесс остановлен!!!!')
        self.textEdit.append('Для новой сессии введите имя директории и нажмите кнопку "Ok".')

    def work_dir(self,text):
        self.auto_sync.workingDirectory=text
    def mirror_dir(self,text):
        self.auto_sync.mirrorDirectory=text
    def closeEvent(self,event):
        self.hide()
        self.mythread.running=False
        self.mythread.wait(5000)
        event.accept()
    def launcher(self):
        if os.name=='posix':
            self.path_list=self.linux_search()
        elif os.name=='nt':
            pass
            #self.path_list=self.win_search()
        self.combo_list+=self.path_list
        self.choice(self.path_list)
    def choice(self, path):
        if len(path)==0:
            self.textEdit.append('Нет доступных адресов')
            self.lineEdit.setText('')
            self.OkBtn.setDisabled(False)            
        else:
            self.textEdit.append('Список доступных адресов синхронизации:')
            for elem in path:
                self.message=str(path.index(elem))+' - '+str(elem)
                self.textEdit.append(self.message)
            self.comboBox_work.addItems(self.combo_list)
            self.comboBox_mirror.addItems(self.combo_list)
            self.textEdit.append('Укажите рабочую директорию и директорию для размещения копий файлов')
 
    def linux_search(self):
        self.username=getpass.getuser()#получение имени пользователя
        self.flash_drivers=os.listdir('/media/{0}'.format(self.username))
        self.path_list=[]
        for i in self.flash_drivers:
            if os.path.exists('/media/{0}/{1}/{2}'.format(self.username,i,self.dir_name)):
                self.path_list.append('/media/{0}/{1}/{2}'.format(self.username,i,self.dir_name))
    #поиск папки <dir_name> в /home/user/
        if os.path.exists('/home/{0}/{1}'.format(self.username,self.dir_name)):
            self.path_list.append('/home/{0}/{1}'.format(self.username,self.dir_name))
        else:
            self.textEdit.append('В разделе /home/{0}/ нет папки "{1}"'.format(self.username,self.dir_name))
        return self.path_list
     


if __name__=='__main__':
    app=QtWidgets.QApplication(sys.argv)
    window=MyWindow()
    window.setFixedSize(443,494)
    window.show()
    sys.exit(app.exec_())

