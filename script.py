#-*- coding:utf-8 -*-
'''
default parameters, you can modify them by
-p '{\"GT_SAMPLE_NAME_2_ID\":\"([0-9]+).txt\",\"DET_SAMPLE_NAME_2_ID\":\"([0-9]+).txt\",\"CONFIDENCES\":true}'

'IOU_CONSTRAINT': 0.5,
'AREA_PRECISION_CONSTRAINT': 0.5,
'GT_SAMPLE_NAME_2_ID': 'gt_img_([0-9]+).txt',
'DET_SAMPLE_NAME_2_ID': 'res_img_([0-9]+).txt',
'LTRB': False,  # LTRB:2points(left,top,right,bottom) or 4 points(x1,y1,x2,y2,x3,y3,x4,y4)
'CRLF': False,  # Lines are delimited by Windows CRLF format
'CONFIDENCES': False,  # Detections must include confidence value. AP will be calculated
'PER_SAMPLE_RESULTS': True  # Generate per sample results and produce data for visualization

'''
import argparse
import rrc_evaluation_funcs

def argparser():
    parse = argparse.ArgumentParser()
    parse.add_argument('-g', dest='g', default='./gt.zip', help="Path of the Ground Truth file. In most cases, the Ground Truth will be included in the same Zip file named 'gt.zip', gt.txt' or 'gt.json'. If not, you will be able to get it on the Downloads page of the Task.")
    parse.add_argument('-s', dest='s', default='./submit.zip', help="Path of your method's results file.")
    parse.add_argument('-o', dest='o', help="Path to a directory where to copy the file 'results.zip' that containts per-sample results.")
    parse.add_argument('-p', dest='p', help="JSON string parameters to override the script default parameters. The parameters that can be overrided are inside the function 'default_evaluation_params' located at the begining of the evaluation Script. use: -p  '{\"CRLF\":true}'")
    parse.add_argument('-c', dest='choice', default='IoU', help="choose algorithm for differet tasks.(Challenges 1、2 use 'DetEva' Challenges 4 use 'IoU', default 'IoU')")
    args = parse.parse_args()
    return args

if __name__=='__main__':
    args = argparser()
    if args.choice=='DetEva':
        from Algorithm_DetEva import default_evaluation_params,validate_data,evaluate_method
    elif args.choice=='IoU':
        from Algorithm_IoU import default_evaluation_params,validate_data,evaluate_method


    rrc_evaluation_funcs.main_evaluation(args,default_evaluation_params,validate_data,evaluate_method)
