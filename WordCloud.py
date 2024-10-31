import matplotlib.pyplot as plt
import jieba.posseg as jp
import numpy as np
import jieba.analyse
import sys
import os
import tkinter as tk
from tkinter import messagebox,filedialog 
from wordcloud import WordCloud
from PIL import Image, ImageTk
from shutil import rmtree
import requests  
from bs4 import BeautifulSoup  
import re  
from gensim.models.ldamodel import LdaModel
from gensim.corpora.dictionary import Dictionary
import pyLDAvis.gensim_models
import webbrowser  

current_path = os.path.dirname(os.path.realpath(sys.argv[0]))
def road(file) :
    return (current_path + '/'+file)
def warning():
    askback = messagebox.askyesno('温馨提示','亲，确认清空文件夹？ (∩＿∩)')
    return askback
def empty_folder(folder_path):
    ask = warning()
    if ask == False:
        return ask
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                rmtree(file_path)
        messagebox.showinfo('succeed',f"成功清空文件夹 {folder_path}!")
    except FileNotFoundError:
        messagebox.showinfo(f"文件夹 {folder_path} 不存在!")
global Text
global ziti
global mask
global picture
global url
global texts
mask = None
Text = road('text/闲情赋.txt')
ziti = road('字体/')
picture = road('WCPictures/')
url = None

texts = open(Text, 'r', encoding='utf-8').read()
# 创建一个GUI窗口
root = tk.Tk()
root.title('PB22061267_周嘉煊_大作业')
  
mode_label = tk.Label(root,text="模式：")
modetype = tk.StringVar(root)  
modetype.set('RGBA')  # 默认值  
mode_options = ['RBGA','RGB']
mode_dropdown = tk.OptionMenu(root,modetype,*mode_options)

language_label = tk.Label(root,text="文本语言：")
languagetype = tk.StringVar(root)  
languagetype.set('中文')  # 默认值  
language_options = ['中文','English']
font_label = tk.Label(root,text="字体：")
fonttype = tk.StringVar(root)

if(languagetype.get() == '中文'):
    fonttype.set('白鸽天行')  # 默认值
    font_options = ['白鸽天行','瘦金加粗','敦煌飞天']
else:
    fonttype.set('TypeWriter')  # 默认值
    font_options = ['TypeWriter','LOVEQueen','NoteScript']
font_dropdown = tk.OptionMenu(root,fonttype,*font_options)  

def on_language_change(a):
    global font_dropdown  
    font_dropdown.destroy()
    if(a == '中文'):
        fonttype.set('白鸽天行')  # 默认值
        font_options = ['白鸽天行','瘦金加粗','敦煌飞天']
    else:
        fonttype.set('TypeWriter')  # 默认值
        font_options = ['TypeWriter','LOVEQueen','NoteScript']   
    font_dropdown = tk.OptionMenu(root,fonttype,*font_options)
    font_dropdown.grid(row=1,column=1)
language_dropdown = tk.OptionMenu(root,languagetype,*language_options,command=on_language_change)
global stopwords
stopwords = set([line.strip() for line in open(road('stopWords.txt'),'r',encoding='utf-8').readlines()])

def ChangeMask():
    if Qmask.get() == True:
        global mask 
        a = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png"),("JPG Files", "*.jpg")],initialdir=current_path)
        if a!= '':
            mask = a
    else:
        mask = None
    ChangeMask_Label.config(text=mask)
    return mask
def ChangeText():
    global Text 
    a = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")],initialdir=current_path)
    if a != '':
        Text = a 
    ChangeText_Label.config(text=Text)
    url = None
    global texts
    texts = open(Text, 'r', encoding='utf-8').read()
    return Text
def ChangePicture():
    global picture 
    a = filedialog.askdirectory(title = "请选择一个文件夹",initialdir=current_path)
    if a!= '' :
        picture = a
    ChangePicture_Label.config(text=picture)
    return picture
def CreateMask():
    new_window = tk.Toplevel(root)  
    new_window.title("新窗口")    
    ImageApp(new_window)  

ChangeMask_button = tk.Button(root, text='选择蒙版',command=ChangeMask)
ChangeMask_Label = tk.Label(root,text=mask)

CreateMask_button = tk.Button(root, text='生成蒙版',command=CreateMask)

ChangeText_button =tk.Button(root, text='选择文本',command=ChangeText)
ChangeText_Label = tk.Label(root,text=Text)

ChangePicture_button = tk.Button(root, text='存储目录',command=ChangePicture)
ChangePicture_Label = tk.Label(root,text=picture)

var = tk.BooleanVar(root,value=True)
checkbox = tk.Checkbutton(root, text='是否保存图片', variable=var)
Qmask = tk.BooleanVar(root,value=False)
MaskCheckbox = tk.Checkbutton(root, text='是否使用蒙版', variable=Qmask)

class ImageApp:  
    def __init__(self, root):  
        self.root = root  
        self.root.title("生成蒙版")  
        def update_value(event=None):  
            """更新标签显示的滑块值"""  
            self.threshold = slider.get()  
            label.config(text=f"当前值: {self.threshold}")
        # 图片显示区域  
        self.base_width = 400
        self.h_size = 300
        self.photo = None
        self.photo2 = None  
        self.label_image = tk.Label(root)  
        self.label_image.grid(row=0,column=0) 
        self.photo_image = tk.Label(root)  
        self.photo_image.grid(row=0,column=1) 
        
        self.threshold = 0
        # 初始状态  
        self.filename = ""   
        self.save_path = None
        # 创建一个滑块（进度条）  
        slider = tk.Scale(root, from_=0, to=255, orient="horizontal", command=update_value)  
        slider.grid(row=1,column=0)  
        
        # 创建一个标签用于显示当前值  
        label = tk.Label(root, text="当前值: 0")  
        label.grid(row=1,column=2)
        # 按钮  
        load_btn = tk.Button(root, text="选择图片", command=self.load_image)  
        load_btn.grid(row=2,column=0)   
        self.load_label = tk.Label(root,text=self.filename)
        self.load_label.grid(row=2,column=1)

        save_btn = tk.Button(root, text="存储位置", command=self.change_save_image)  
        save_btn.grid(row=3,column=0)  
        self.save_label = tk.Label(root,text=self.save_path)
        self.save_label.grid(row=3,column=1)

        create_btn = tk.Button(root, text="预览蒙版", command=self.create_image)  
        create_btn.grid(row=4,column=0)

        download_btn = tk.Button(root, text="保存蒙版", command=self.save_image)  
        download_btn.grid(row=4,column=1)
 
    def load_image(self):  
        self.filename = filedialog.askopenfilename()  
        if self.filename:  
            # 使用Pillow打开图片，并转换为Tkinter可接受的格式  
            img = Image.open(self.filename)  
            self.h_size = int((float(img.size[1])/float(img.size[0]) *self.base_width ))
            img = img.resize((self.base_width, self.h_size))  # 可选：调整图片大小  
            self.photo = ImageTk.PhotoImage(img)  
            # 更新Label以显示新图片  
            self.load_label.config(text = self.filename)
            self.label_image.config(image=self.photo)  
            self.label_image.image = self.photo
    def create_image(self):
        img = Image.open(self.filename).convert('L')
        table = []
        for i in range(256):
            if i < self.threshold:
                table.append(0)
            else:
                table.append(255)
        # 图片二值化
        self.photo2 = img.point(table, 'L')
        self.photo2 = self.photo2.resize((self.base_width, self.h_size))
        a = ImageTk.PhotoImage(self.photo2)
        self.photo_image.config(image= a)
        self.label_image.image = a
    def change_save_image(self):  
        a = filedialog.askdirectory(title = "请选择一个文件夹",initialdir=current_path)
        if a!= '' :
            self.save_path = a
        self.save_label.config(text=self.save_path)
    def save_image(self):  
        self.photo2.save(self.save_path+'/'+self.filename.split('/')[-1])

def empty_folder():
    ask = warning()
    if ask == False:
        return ask
    folder_path = picture
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                rmtree(file_path)
        messagebox.showinfo('succeed',f"成功清空文件夹 {folder_path}!")
    except FileNotFoundError:
        print(f"文件夹 {folder_path} 不存在!")

del_button = tk.Button(root, text="清空图片",command= empty_folder) 

name_label = tk.Label(root,text='name:')
name_entry = tk.Entry(root)
def analysis():
    global texts
    flags = ('n', 'nr', 'ns', 'nt', 'eng', 'v', 'd','vn','vd')
    words = [[word.word for word in jp.cut(texts) if word.flag in flags and word.word not in stopwords]]
    dictionary = Dictionary(words)
    corpus = [dictionary.doc2bow(words[0])]
    lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=5, random_state=100, iterations=50)
    plot =pyLDAvis.gensim_models.prepare(lda,corpus,dictionary)
    save_html = road('主题分析/')+Text.split('/')[-1].split('.')[0]+'.html'
    pyLDAvis.save_html(plot,save_html)
    webbrowser.open(save_html)

analysis_button = tk.Button(root,text='主题分析',command = analysis)

def CreateCloud(): 
    global Text 
    global texts 
    name = name_entry.get()
    if name == '':
        name = Text.split('/')[-1].split('.')[0]
    # 中文分词
    global mask
    freq = jieba.analyse.extract_tags(texts, topK=200, withWeight=True)
    freq = {i[0]: i[1] for i in freq if i[0] not in stopwords}

    Mask = np.array(Image.open(mask)) if mask != None else None
    global stopwords
    wc = WordCloud(mask = Mask,font_path=ziti+fonttype.get()+".ttf", mode=modetype.get(), background_color=None,stopwords = stopwords).generate_from_frequencies(freq)
    if var.get() is True:
        wc.to_file(picture+name+".png")
    # 显示词云
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.show()

def fetch_chinese_text(url):  
    response = requests.get(url)  
    response.raise_for_status()  # 如果请求失败，抛出HTTPError异常  
    soup = BeautifulSoup(response.text, 'html.parser')  
    text = soup.get_text()  
    chinese_text = re.findall(r'[\u4e00-\u9fa5，。？！“”‘’]', text)  
    chinese_text_str = ''.join(chinese_text)  
    return chinese_text_str  
def create_popup():  
    # 创建一个Toplevel窗口作为弹窗  
    popup = tk.Toplevel()  
    popup.title("抓取网页（中文）")  
    # 在弹窗中添加一个输入框  
    entry = tk.Entry(popup)  
    entry.pack(pady=20)  
    # 添加一个按钮，点击时获取输入框的值并关闭弹窗  
    def on_submit():  
        global url
        global texts
        url = entry.get()      
        texts = fetch_chinese_text(url)
        if texts == '':
            messagebox.showinfo('目标网页无法解析出中文\\可能为全英网页或被加密处理')
        ChangeText_Label.config(text=url)
        CreateCloud()
        popup.destroy()  # 关闭弹窗  
    submit_button = tk.Button(popup, text="提交", command=on_submit)  
    submit_button.pack(pady=10)  
  
# 创建一个按钮，点击时调用create_popup函数  
UrlButton = tk.Button(root, text="制作中文网页词云", command=create_popup)

CreateCloud_button = tk.Button(root, text="生成词云", command=CreateCloud)

name_label.grid(row=0, column=0)
name_entry.grid(row=0, column=1)
checkbox.grid(row=0, column=2)

font_label.grid(row=1, column=0)
font_dropdown.grid(row=1,column=1)

mode_label.grid(row=1, column=2)
mode_dropdown.grid(row=1,column=3)

language_label.grid(row=2, column=0)
language_dropdown.grid(row=2,column=1)
MaskCheckbox.grid(row=2,column=2)

ChangeMask_button.grid(row=3, column=0)
ChangeMask_Label.grid(row=3, column=1)

ChangePicture_button.grid(row=4, column=0)
ChangePicture_Label.grid(row=4, column=1)

ChangeText_button.grid(row=5, column=0)
ChangeText_Label.grid(row=5, column=1)

del_button.grid(row=6,column=0)
UrlButton.grid(row=6, column = 1)
CreateMask_button.grid(row= 6,column=2)

CreateCloud_button.grid(row=7, column=0) 
analysis_button.grid(row=7,column=1)
# 运行GUI窗口  
root.mainloop()