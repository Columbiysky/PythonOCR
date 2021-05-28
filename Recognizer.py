import easyocr
import cv2
import pdf2image
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageEnhance
import os
import pytesseract as pt
import re

def sort_contours(cnts, method="left-to-right"):
    # initialize the reverse flag and sort index
    reverse = False
    i = 0
    # handle if we need to sort in reverse
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True
    # handle if we are sorting against the y-coordinate rather than
    # the x-coordinate of the bounding box
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
    # construct the list of bounding boxes and sort them from top to
    # bottom
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
    key=lambda b:b[1][i], reverse=reverse))
    # return the list of sorted contours and bounding boxes
    return (cnts, boundingBoxes)

def DrawRecognizedText(img, coords_text):
    imgg = img
    for coord,text in coords_text.items():
        x,y = coord
        # вывести распознанный текст выше оригинального
        cv2.putText(img, text, (x+30, y+10),
            cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 0, 0), 2)
    # вывести итоговое изображение
    plt.figure(figsize=[20,30])
    plt.imshow(imgg, cmap='jet')

def MakeBordersBetter(imgPath, direction):
    if direction == 'vertical':
        img = cv2.imread(imgPath)        
        
        x_coords = []
        all_line_coords = []
        for y in range(img.shape[0]):
            for x in range(img.shape[1]):
                for color in img[y,x]:
                    if color > 200:
                        all_line_coords.append(list([y,x]))
                        x_coords.append(x)
                        break
        x_classes = list(set([int(x/100) for x in x_coords]))
        
        x_coords_by_class = {}
        for x_class in x_classes:
            x_coords_by_class[x_class] = [i for i in all_line_coords if int(i[1]/100)==x_class]
        
        min_xy_by_class = {}
        max_xy_by_class = {}
        for key in x_coords_by_class.keys():
            min_y = max(img.shape)
            max_y = 0

            min_x = max(img.shape)
            max_x = 0

            for val in x_coords_by_class[key]:
                if val[0] < min_y:
                    min_y = val[0]
                if val[0] > max_y:
                    max_y = val[0]

                if val[1] < min_x:
                    min_x = val[1]
                if val[1] > max_x:
                    max_x = val[1]

            min_xy_by_class[key] = (min_y,min_x)
            max_xy_by_class[key] = (max_y,max_x)
            
            
        for key in min_xy_by_class:
            diff = max_xy_by_class[key][1] - min_xy_by_class[key][1]
            if diff != 0 and diff < 2:
                img = cv2.line(img,(min_xy_by_class[key][1],min_xy_by_class[key][0]),
                           (max_xy_by_class[key][1], max_xy_by_class[key][0]),(255,255,255), diff)
            else:
                img = cv2.line(img,(min_xy_by_class[key][1],min_xy_by_class[key][0]),
                           (max_xy_by_class[key][1], max_xy_by_class[key][0]),(255,255,255), 2)
        cv2.imwrite('./Temp/vertical.png',img)
    
    if direction == 'horizontal':
        img = cv2.imread(imgPath)
        
        y_coords = []
        all_line_coords= []
        for x in range(img.shape[1]):
            for y in range(img.shape[0]):
                for color in img[y,x]:
                    if color > 240:
                        all_line_coords.append(list([y,x]))
                        y_coords.append(y)
                        break
        y_classes = list(set([round(y/10) for y in y_coords]))
        xycoords_by_class = {}
        for y_class in y_classes:
            xycoords_by_class[y_class] = [i for i in all_line_coords if round(i[0]/10)==y_class] 
        
        min_xy_by_class = {}
        max_xy_by_class = {}
        for key in xycoords_by_class.keys():
            min_y = max(img.shape)
            max_y = 0

            min_x = max(img.shape)
            max_x = 0

            for val in xycoords_by_class[key]:
                if val[0] < min_y:
                    min_y = val[0]
                if val[0] > max_y and val[0] - min_y < 5:
                    max_y = val[0]

                if val[1] < min_x:
                    min_x = val[1]
                if val[1] > max_x:
                    max_x = val[1]

            min_xy_by_class[key] = (min_y,min_x)
            max_xy_by_class[key] = (max_y,max_x)
            
        for key in max_xy_by_class.keys():
            if max_xy_by_class[key][0] - min_xy_by_class[key][0] > 2 :
                max_xy_by_class.update({key : (min_xy_by_class[key][0] + 1, max_xy_by_class[key][1])})
        
        for key in min_xy_by_class:
            diff = max_xy_by_class[key][0] - min_xy_by_class[key][0]
            if diff != 0 and diff < 2:
                img = cv2.line(img,(min_xy_by_class[key][1],max_xy_by_class[key][0]),
                           (max_xy_by_class[key][1], max_xy_by_class[key][0]),(255,255,255)#, 2)
                            ,diff)
            else:
                img = cv2.line(img,(min_xy_by_class[key][1],max_xy_by_class[key][0]),
                           (max_xy_by_class[key][1], max_xy_by_class[key][0]),(255,255,255), 2)
        cv2.imwrite('./Temp/horizontal.png', img)

def main():
    pt.pytesseract.tesseract_cmd =  r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    images = pdf2image.convert_from_path(r"D:\diploma\pythonOCR\Universities\Московской области Университет Дубна\Stoimost_obuch_07.10.2019.pdf", poppler_path = r"C:\Users\Columbiysky\poppler-0.68.0\bin")
    old_level = ''
    old_time = ''
    old_study_type = ''
    old_course = 0
    university_dict = {}
    countList = 0
    old_foreign = ''
    for img_elem in images:
        countList = countList + 1 
        level = ''
        time = ''
        study_type = ''
        course = 0
        foreign = False
        if(os.path.exists('./Temp')):
            img_elem.save('./Temp/tmp.png') # сохраняем исходное изображение
            im = Image.open('./Temp/tmp.png') # открываем через pillow
            enhancer = ImageEnhance.Contrast(im) # инициализируем экземпляр увеличения контрастности, 
                                                # передав изображение в конструктор
            enhanced_cont = enhancer.enhance(4.0) # увеличиваем контрастность на изображении
            enhancer = ImageEnhance.Sharpness(enhanced_cont) # инициализируем экземпляр увеличения резкости, 
                                                # передав изображение в конструктор
            enhanced_cont_sharped = enhancer.enhance(2) # увеличиваем резкость
            enhanced_cont_sharped.save('./Temp/enhanced_contrast4_sharped2.png') # сохраняем изображение
            img = cv2.imread('./Temp/enhanced_contrast4_sharped2.png',0) # открываем изображение через openCV
        else:
            os.mkdir('Temp')
            img_elem.save('./Temp/tmp.png')
            im = Image.open('./Temp/tmp.png')
            enhancer = ImageEnhance.Contrast(im)
            enhanced_cont = enhancer.enhance(4.0)
            enhancer = ImageEnhance.Sharpness(enhanced_cont)
            enhanced_cont_sharped = enhancer.enhance(2)
            enhanced_cont_sharped.save('./Temp/enhanced_contrast4_sharped2.png')
            img = cv2.imread('./Temp/enhanced_contrast4_sharped2.png',0)
            #print(img.shape)
            
        #thresholding the image to a binary image
        thresh,img_bin = cv2.threshold(img,128,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        #inverting the image
        img_bin = 255-img_bin
        cv2.imwrite('./Temp/cv_inverted.png',img_bin)
        
        # Длина ядра равна  сотой части общей ширины
        kernel_len = np.array(img).shape[1]//100
        # Определение структурирующего элемента для обнаружения всех вертикальных линий изображения 
        ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len))
        # Определение структурирующего элемента для обнаружения всех горизонтальных линий изображения
        hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))
        
        #находим вертикальные линии
        image_1 = cv2.erode(img_bin, ver_kernel, iterations=3)
        vertical_lines = cv2.dilate(image_1, ver_kernel, iterations=3)
        cv2.imwrite("./Temp/vertical.jpg",vertical_lines)
        
        #находим горизонтальные линии
        image_2 = cv2.erode(img_bin, hor_kernel, iterations=3)
        horizontal_lines = cv2.dilate(image_2, hor_kernel, iterations=3)
        cv2.imwrite("./Temp/horizontal.jpg",horizontal_lines)
        
        #Make the borders thicker
        MakeBordersBetter('./Temp/vertical.jpg','vertical')
        MakeBordersBetter('./Temp/horizontal.jpg','horizontal')
        
        #Override lines
        vertical_lines = cv2.imread('./Temp/vertical.png')
        horizontal_lines = cv2.imread('./Temp/horizontal.png')
        
        # Combine horizontal and vertical lines in a new third image, with both having same weight.
        img_vh = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)
        img_vh = cv2.cvtColor(img_vh, cv2.COLOR_BGR2GRAY)
        #Eroding and thesholding the image
        img_vh = cv2.erode(~img_vh, kernel, iterations=2)
        thresh, img_vh = cv2.threshold(img_vh,127,255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        cv2.imwrite("./Temp/img_vh.jpg", img_vh)
        bitxor = cv2.bitwise_xor(img,img_vh)
        bitnot = cv2.bitwise_not(bitxor)
        
        contours, hierarchy = cv2.findContours(img_vh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort all the contours by top to bottom.
        contours, boundingBoxes = sort_contours(contours, method="top-to-bottom")
        
        #Creating a list of heights for all detected boxes
        heights = [boundingBoxes[i][3] for i in range(len(boundingBoxes))]
        
        #Get mean of heights
        mean = np.mean(heights)
        
        #Create list box to store all boxes in  
        box = []
        # Get position (x,y), width and height for every contour and show the contour on image
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if (w<1000 and h<500):
                image = cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                box.append([x,y,w,h])
                
        #Creating two lists to define row and column in which cell is located
        row=[]
        column=[]
        j=0
        
        #Sorting the boxes to their respective row and column
        for i in range(len(box)):    
            if(i==0):
                column.append(box[i])
                previous=box[i]    
            else:
                if(box[i][1]<=previous[1]+mean/2):
                    column.append(box[i])
                    previous=box[i]            

                    if(i==len(box)-1):
                        row.append(column)        

                else:
                    row.append(column)
                    column=[]
                    previous = box[i]
                    column.append(box[i])
                    
        #calculating maximum number of cells
        countcol = 0
        for i in range(len(row)):
            countcol = len(row[i])
            if countcol > countcol:
                countcol = countcol
                
        #Retrieving the center of each column
        center = [int(row[i][j][0]+row[i][j][2]/2) for j in range(len(row[i])) if row[0]]    
        center=np.array(center)
        center.sort()
        
        #Regarding the distance to the columns center, the boxes are arranged in respective order
        finalboxes = []
        for i in range(len(row)):
            lis=[]
            for k in range(countcol):
                lis.append([])
            for j in range(len(row[i])):
                diff = abs(center-(row[i][j][0]+row[i][j][2]/4))
                minimum = min(diff)
                indexing = list(diff).index(minimum)
                lis[indexing].append(row[i][j])
            finalboxes.append(lis)
            
        #Recognizing text in boxes
        outer=[]
        outer_2 = []
        coords_text_eo = {}
        coords_text_pt = {}
        reader = easyocr.Reader(['ru'])
        for i in range(len(finalboxes)):
            for j in range(len(finalboxes[i])):
                inner=''
                if(len(finalboxes[i][j])==0):
                    outer.append(' ')
                else:
                    for k in range(len(finalboxes[i][j])):
                        tmpTxt = ''
                        y,x,w,h = finalboxes[i][j][k][0],finalboxes[i][j][k][1], finalboxes[i][j][k][2],finalboxes[i][j][k][3]
                        finalimg = bitnot[x:x+h, y:y+w]
                        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
                        border = cv2.copyMakeBorder(finalimg,2,2,2,2, cv2.BORDER_CONSTANT,value=[255,255])
                        resizing = cv2.resize(border, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                        dilation = cv2.dilate(resizing, kernel,iterations=1)
                        erosion = cv2.erode(dilation, kernel,iterations=2)

                        out_eo = reader.readtext(erosion)
                        out_pt = pt.image_to_string(erosion, lang='rus')
                        for (bbox, text, prob) in out_eo:
                            coords_text_eo[(y,x)] = text.lstrip().rstrip()
                        res = ''
                        out_pt = out_pt.replace('\n','').replace('_','').replace('|','').replace('—','').lstrip().rstrip()
                        if(out_pt == ' ' or out_pt == '\n' or out_pt == None):
                            res = '\0'
                        else:
                            res = out_pt
                        coords_text_pt[(y,x)] =  res
        
        #Configuring dict[(coords)]=recognized_value
        coords_result = {}
        result_str = ''
        count = 0
        for k,v in coords_text_pt.items():
            for kk, vv in coords_text_eo.items():
                if(k==kk):
                    if (any(map(str.isdigit, v)) or any(map(str.isdigit, vv))):
                        if(len(v)<len(vv) and v != '' and v != '\n' and v != None): 
                            result_str = v.replace('.','').replace('=','').replace(' ','').replace('_','').lstrip()
                        else: 
                            result_str = vv.replace('.','').replace('=','').replace(' ','').replace('_','').lstrip()
                    else:
                        v = v.replace('.','').replace('=','').replace('?','').replace('_','').lstrip()
                        vv = vv.replace('.','').replace('=','').replace('?','').replace('_','').lstrip()
                        try:
                            if v != '' and v != None and len(v) > 0:
                                while(v[0].isalpha() == False and len(v) > 0):
                                    v = v[1:]

                            if vv != '' and vv != None and len(vv) > 0:
                                while(vv[0].isalpha() == False and len(vv) > 0 ):
                                    vv = vv[1:]
                        except IndexError:
                            print('v = ' +v + '; vv = ' + vv + '; page = '+ str(countList))
                        if(len(v) < len(vv) and len(v) > 0):
                            s1 = re.sub(r"[^а-яА-Я()]+", "", v)
                            s2 = re.sub(r"[^а-яА-Я()]+", "", vv)
                            if(len(v) > 0):
                                percent  = sum([l1 == l2 for l1, l2 in zip(s1, s2)])/len(v)
                            else:
                                percent = 1
                            if percent > 0.6 or vv.find(v) > -1:
                                result_str = vv
                        else:
                            s1 = re.sub(r"[^а-яА-Я()]+", "", v)
                            s2 = re.sub(r"[^а-яА-Я()]+", "", vv)
                            if(len(vv) > 0):
                                percent = sum([l1 == l2 for l1, l2 in zip(s1, s2)])/len(vv)
                            else:
                                percent = 1
                            if  percent > 0.6 or v.find(vv) > -1:
                                result_str = v
                    coords_result[k] = result_str
        
        #configuring two dicts first with text only, second with  
        prices_dict = {}
        text_dict = {}
        for k,v in coords_result.items():
            if (any(map(str.isdigit, v))):
                prices_dict[k] = v
            else:
                text_dict[k] = v            
        
        #configuring ordinate list of all prices
        prices_y_keys_list = []
        for i in list(prices_dict.keys()):
            prices_y_keys_list.append(i[1])
        
        #configuring two dicts one withouth price, second with price
        no_price_items = {}
        items_price = {}
        for k,v in text_dict.items():
            price_y_val = min(prices_y_keys_list, key=lambda x:abs(x-k[1]))
            if abs(k[1] - price_y_val) > 10:
                no_price_items[k] = v
                
                if v.lower().replace(' ','').find('семестр') > -1:
                    time = 'Семестр'
                if v.lower().replace(' ','').find('год') > -1:
                    time = 'Год'     
                    
                if v.lower().find('бакалавр') > -1:
                    level = 'Бакалавриат'
                if v.lower().find('специал') > -1:
                    level = 'Специалитет'
                if v.lower().find('магистр') > -1:
                    level = 'Магистратура'
                
                
                if v.lower().find('очно-заочная') > -1 or v.lower().find('очно-заочной') > -1:
                    study_type = 'Очно-заочная'
                elif v.lower().find('заочная') > -1 or v.lower().find('заочной') > -1:
                    study_type = 'Заочная'
                elif v.lower().find('очная') > -1 or v.lower().find('очной') > -1:
                    study_type = 'Очная'
                
                
                if v.lower().replace(' ','').find('первогокурса') > -1:
                    course = 1
                elif v.lower().replace(' ','').find('второгокурса') > -1:
                    course = 2
                elif v.lower().replace(' ','').find('третьегокурса') > -1:
                    course = 3
                elif v.lower().replace(' ','').find('четвертогокурса') > -1:
                    course = 4
                elif v.lower().replace(' ','').find('пятогокурса') > -1:
                    course = 5
                elif v.lower().replace(' ','').find('шестогокурса') > -1:
                    course = 6
                elif v.lower().find('четвертогоипятогокурсов') > -1:
                        course = 45
                
                if level != '' and level != None:
                    old_level = level

                if course != 0:
                    old_course = course

                if study_type != '' and study_type != None:
                    old_study_type = study_type
            else:
                key = (0,0)
                for i in list(prices_dict.keys()):
                    if i[1] == price_y_val:
                        key = i
                        
                if (study_type == '' or study_type == None) and course == 0:
                    #checking where is top box of the table      
                    #setting course, study level, and study type 
                    table_start_y = list(text_dict.keys())[0][1]
                    img = cv2.imread('./Temp/enhanced_contrast4_sharped2.png',0)
                    no_table_img = img[0:table_start_y,:]
                    #plt.figure(figsize=(20,30))
                    #plt.imshow(no_table_img, cmap = 'gray')
                    res_pt = pt.image_to_string(no_table_img, lang='rus')
                    if res_pt != None and res_pt != '': 
                        if res_pt.lower().find('очно-заочной') > -1:
                            study_type = 'очно-заочной'
                        elif res_pt.lower().find('заочной') > -1:
                            study_type = 'заочной'
                        elif res_pt.lower().find('очной') > -1:
                            study_type = 'очной' 

                        if res_pt.lower().find('первого курса') > -1:
                            course = 1
                        elif res_pt.lower().find('второго курса') > -1:
                            course = 2
                        elif res_pt.lower().find('третьего курса') > -1:
                            course = 3
                        elif res_pt.lower().find('четвертого курса') > -1:
                            course = 4
                        elif res_pt.lower().find('пятого курса') > -1:
                            course = 5
                        elif res_pt.lower().find('шестого курса') > -1:
                            course = 6
                        elif res_pt.lower().find('четвертого и пятого курсов') > -1:
                            course = 45

                        if res_pt.lower().find('иностранных') > -1:
                            foreign = True
                            old_foreign = True
                        else:
                            foreign = False

                        if course != 0:
                            old_course = course
                        else:
                            course = old_course
                        if study_type != '' and study_type != None:
                            old_study_type = study_type
                        else:
                            study_type = old_study_type
                        if level != '' and level != None:
                            old_level = level
                        else:
                            level = old_level
                    else:
                        course = old_course
                        study_type = old_study_type
                        level = old_level    
                        foreign = old_foreign
                    
                    if(foreign == True):
                        items_price[str(v) + ';'+ level + ';' + str(course) + ';' + study_type + ';f'] = prices_dict[key]
                    else:
                        items_price[str(v) + ';'+ level + ';' + str(course) + ';' + study_type + ';p'] = prices_dict[key]
                else:
                    items_price[str(v) + ';'+ level + ';' + str(course) +  ';' +study_type + ';p'] = prices_dict[key]
        
        for k,v in items_price.items():
            university_dict[k] = v

        f = open('uni_prices.txt','w',encoding = 'windows-1251')
        for k,v in university_dict.items():
            f.write(k + ';' + v + '\n')
        f.close()

if __name__ == '__main__':
    main()