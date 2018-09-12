#-*- coding:utf-8 -*-
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
