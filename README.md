MODIFIED BY [ICDAR CODES](http://rrc.cvc.uab.es/?com=introduction)
INSTRUCTIONS FOR THE STANDALONE SCRIPTS

### HOW TO USE
Requirements:
- Python version 2.7.
- Each Task requires different Python modules. When running the script, if some module is not installed you will see a notification and installation instructions.
 
Procedure:
Download the ZIP file for the requested script and unzip it to a directory.
 
Open a terminal in the directory and run the command:

**python script.py –g gt.zip –s submit.zip**
 
If you have already installed all the required modules, then you will see the method’s results or an error message if the submitted file is not correct.
 
parameters:

-g: Path of the Ground Truth file. In most cases, the Ground Truth will be included in the same Zip file named 'gt.zip', gt.txt' or 'gt.json'. If not, you will be able to get it on the Downloads page of the Task.

-s: Path of your method's results file.
 
Optional parameters:

-o: Path to a directory where to copy the file ‘results.zip’ that contains per-sample results.

-p: JSON string parameters to override the script default parameters. The parameters that can be overrided are inside the function 'default_evaluation_params' located at the begining of the evaluation Script.


```
when use Algorithm_IOU -p
'IOU_CONSTRAINT': 0.5,
'AREA_PRECISION_CONSTRAINT': 0.5,
'GT_SAMPLE_NAME_2_ID': 'gt_img_([0-9]+).txt',
'DET_SAMPLE_NAME_2_ID': 'res_img_([0-9]+).txt',
'LTRB': False,  # LTRB:2points(left,top,right,bottom) or 4 points(x1,y1,x2,y2,x3,y3,x4,y4)
'CRLF': False,  # Lines are delimited by Windows CRLF format
'CONFIDENCES': False,  # Detections must include confidence value. AP will be calculated
'PER_SAMPLE_RESULTS': True,  # Generate per sample results and produce data for visualization
'E2E': False   #compute average edit distance for end to end evaluation
```
```
when use Algorithm_DetEva -p
'AREA_RECALL_CONSTRAINT': 0.8,
'AREA_PRECISION_CONSTRAINT': 0.4,
'EV_PARAM_IND_CENTER_DIFF_THR': 1,
'MTYPE_OO_O': 1.,
'MTYPE_OM_O': 0.8,
'MTYPE_OM_M': 1.,
'GT_SAMPLE_NAME_2_ID': 'gt_img_([0-9]+).txt',
'DET_SAMPLE_NAME_2_ID': 'res_img_([0-9]+).txt',
'CRLF': False  # Lines are delimited by Windows CRLF format
```

-c: choose algorithm for differet tasks.(Challenges 1、2 use 'DetEva' Challenges 4 use 'IoU', default 'IoU')
 
**Example: python script.py –g gt.zip –s submit.zip –o ./ -p  '{\"CRLF\":true}' -c DetEva**


### THEORY
see [my blog](https://blog.csdn.net/liuxiaoheng1992/article/details/82632594)
