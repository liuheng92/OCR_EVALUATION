MODIFIED BY [ICDAR CODES](http://rrc.cvc.uab.es/?com=introduction)
INSTRUCTIONS FOR THE STANDALONE SCRIPTS

### HOW TO USE
Requirements:
-         Python version 2.7.
-         Each Task requires different Python modules. When running the script, if some module is not installed you will see a notification and installation instructions.
 
Procedure:
Download the ZIP file for the requested script and unzip it to a directory.
 
Open a terminal in the directory and run the command:
python script.py –g gt.zip –s submit.zip
 
If you have already installed all the required modules, then you will see the method’s results or an error message if the submitted file is not correct.
 
parameters:
-g: Path of the Ground Truth file. In most cases, the Ground Truth will be included in the same Zip file named 'gt.zip', gt.txt' or 'gt.json'. If not, you will be able to get it on the Downloads page of the Task.
-s: Path of your method's results file.
 
Optional parameters:
-o: Path to a directory where to copy the file ‘results.zip’ that contains per-sample results.
-p: JSON string parameters to override the script default parameters. The parameters that can be overrided are inside the function 'default_evaluation_params' located at the begining of the evaluation Script.
-c: choose algorithm for differet tasks.(Challenges 1、2 use 'DetEva' Challenges 4 use 'IoU', default 'IoU')
 
Example: python script.py –g gt.zip –s submit.zip –o ./ -p  '{\"CRLF\":true}' -c 'DetEva'


### THEROY
在ICDAR的一个答疑网页([F.A.Q](http://rrc.cvc.uab.es/?com=faq))中有相关介绍，其中文本定位分为几个挑战，分别称为Challenges 1、Challenges 2和Challenges 4，不同的挑战有不同的评价方法。

下面先简单介绍一下这三个挑战：
Challenges 1(Born-Digital)的数据来源于电脑制作的，而Challenges 2和Challenges 4(Real Scene)的数据要源于摄像机的拍摄。其中Challenges 2主要是来源于用户有意识的对焦拍摄的(focused text)比如一些翻译的场景，这些场景中文字基本是对焦好的且水平的，Challenges 4主要来源也是用户拍摄的，但是这些照片的拍摄是比较随意的(incidental text)这样会导致图片里的文字角度、清晰度、大小等情况非常的多。

针对不同的挑战，评价检测算法的方法就不相同：

1. Challenges 1和2使用的是叫做 [DetEva](https://perso.liris.cnrs.fr/christian.wolf/software/deteval/index.html)的方法，该方法来自2006年C. Wolf的一篇文章《Object Count / Area Graphs for the Evaluation of Object Detection and Segmentation Algorithms》，ICDAR自己实现了一套DetEva方法([下载地址](http://rrc.cvc.uab.es/?ch=2&com=mymethods&task=1))

2. Challenges 4使用的是简单的通过IoU来判定算法的recall、precision的。([下载地址](http://rrc.cvc.uab.es/?ch=4&com=mymethods&task=1))

***注意：必须先注册才能下载***

下面讲一下两个评测方法：
1.Challenges 1和2使用的评测方法(即DetEva)

![1.png](https://upload-images.jianshu.io/upload_images/6983308-4eb52a8099a6f875.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


如上图所示，文章考虑三种情况来判断标定框与检测框是否匹配(match)：

* 一对一的match，如(a)所示
* 一对多的match，如(b)所示，ground truth 粒度大于detection 粒度时出现的情况。
* 多对一的match，如(c)所示，detection的粒度大于ground truth的粒度

***注意：这里的框无论是标定框还是检测框都认为是水平的矩形框，且该评测方法并不考虑多对多的情况。***

具体做法*(对于每张图像)*：

1. 创建![](http://latex.codecogs.com/gif.latex?\n \\times m)大小的两个矩阵分别叫做recallMat、precisionMat，其中n为标定框(ground truth)的个数，m为检测到的框个数

* recallMat中存储的是每个检测框的召回率，计算方法为![](http://latex.codecogs.com/gif.latex?\recallMat_{i,j}=\\frac {area(inter(gt_{i},det_{j}))}{area(gt_{i})})，其中area()函数表示求矩形的面积，inter()函数表示求两个矩形的交集，![](http://latex.codecogs.com/gif.latex?\gt_{i})表示第i个标定框，![](http://latex.codecogs.com/gif.latex?\det_{j})表示第j个标定框

* precisionMat中存储的是每个检测框的准确率，计算方法为![](http://latex.codecogs.com/gif.latex?\precisionMat_{i,j}=\\frac {area(inter(gt_{i},det_{j}))}{area(det_{j})})，其中的符号定义同上

2. 在考虑三种情况之前，先要定义两个域值这里称为r和p，r表示判断召回率的阈值这里设为0.8，p表示判断准确率的阈值这里设为0.4，recall用来存储召回率，precision用了存储准确率

3. one-to-one matches，如果在recallMat和precisionMat中的i行只有一个值大于阈值，j列中也只有一个值大于阈值，且这个值在第i行第j列，那么就认为![](http://latex.codecogs.com/gif.latex?\gt_{i})与![](http://latex.codecogs.com/gif.latex?\det_{j})是one-to-one matches。如果![](http://latex.codecogs.com/gif.latex?\gt_{i})与![](http://latex.codecogs.com/gif.latex?\det_{j})满足一定的条件就将recall和precision加1

* 这里说的一定条件是指两个框的中心点距离与两个框对角线平均值的比例要小于阈值1

4. one-to-many matches，对于precisionMat中如果i行中有多个值大于p，将这些值相加，用最后的和与r比较，如果大于r就符合one-to-many matches的条件，one就是![](http://latex.codecogs.com/gif.latex?\gt_{i})，many就是i行中所有大于p值的列对应的框。如果满足one-to-many matches就将recall加0.8，precision加![](http://latex.codecogs.com/gif.latex?\0.8\\times num)，$num$表示对应与![](http://latex.codecogs.com/gif.latex?\gt_{i})匹配的所有many框的个数(说白了就是many的具体值)

5. many-to-one matches，这里与one-to-many matches类似，只是先判断recallMall中j列，将j列中所有大于r的值相加，用最后的和与p比较，如果大于p就认为符合many-to-one matches的条件，one就是指![](http://latex.codecogs.com/gif.latex?\det_{j})，many值的是j列中所有大于r值对应的框。如果满足many-to-one matches就将recall加![](http://latex.codecogs.com/gif.latex?\1*y)(与上述x相同，y表示many的具体值)，precision加1

6. 最后用recall除以所有的gt个数(这个个数不是n，n代表该张图片所有标定框的个数，但是计算的时候会将文本标定为###的框去除)，同理precision也会除以所有的det的个数(这个个数也不为m，如果有检测框检测到###区域，这个检测框也认为无效)。f-score也就是hmean算法为recall和precision的调和平均数。

*这里要说明一下的是，为什么有时候recall和precision加1有时候加0.8，可以认为是对不同匹配结果的惩罚。还有上面说明的是一张图片的recall和precision计算方法，如果是整个数据集也是类似，只是先将第5步求出的recall和precision相加最后除以整个数据集的gt个数和det个数。*

到这里Challenges 1和2使用的评测方法就讲完了

2.Challenges 4使用的评测方法
不同于Challenges 1和2的是Challenges 4标定的框多种多样，并不是水平的，如果像之前那样可能各种匹配形式会很复杂，Challenges 4的评测方法采用简单的计算IoU来进行评测，在Challenges 4中标定框与检测框都为多边形而不是之前的水平矩形了。

具体做法*(对于每张图像,不同于)*：

1. 创建![](http://latex.codecogs.com/gif.latex?\n\\times m)大小的一个矩阵叫做iouMat，其中n为标定框(ground truth)的个数，m为检测到的框个数
* 计算方法为![](http://latex.codecogs.com/gif.latex?\iouMat_{i,j}=\\frac {area(inter(gt_{i},det_{j}))}{area(union(gt_{i},det_{j}))})，公式中的符号与之前描述一样，union表示两个多边形的并集

2. 定义IoU阈值0.5

3. 在iouMat中，统计大于0.5的个数，将这个值除以gt个数(这里的gt个数同上，除去了文本标定为###的框)得到recall，除以det的个数(这个个数也同上)得到precision。到这里就求出了recall和precision，但是Challenges 4还增加了map的指标

4. 如果要计算map那么在检测的输出结果中要输出一列每个检测框的置信度，将每个符合条件(这里的条件就是3中大于0.5的检测框)的框的置信度相加，除以满足条件的总的置信度大于零的框的个数，最后除以除以gt个数(这里的gt个数同上，除去了文本标定为###的框)，得到每张图片的map指标。若要算整个测试集的map，同理，只是框个数变成的整个测试集的框个数。

*要说明的是，如果检测到的是长文本，但是标定的是单个字，这时候检测可能会算为检测不准确，这是这个评测方法的缺陷*

到这里Challenges 4使用的评测方法就讲完了
