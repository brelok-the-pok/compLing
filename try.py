# from subprocess import Popen, PIPE, STDOUT
# from tqdm.auto import trange
# import sys, re
# i = input()
#
#
# def work(i):
#     delimiter = '<end of news>'
#     file = open('newsTexts/allNewsRaw.txt', 'r')
#     news = file.read().split(delimiter)
#     file.close()
#     n = len(news)
#
#     start_list = \
#         [0, int(n / 8) + 1, int(n / 4) + 1, int(n / 2) + 1, int(n / 1.6) + 1, int(n * 3 / 4) + 1, int(n * 0.875) + 1]
#     end_list = [int(n / 8), int(n / 4), int(n / 2), int(n / 1.6), int(n * 3 / 4), int(n * 0.875), n]
#     files_list = ['parse/1', 'parse/2', 'parse/3', 'parse/4', 'parse/5', 'parse/6', 'parse/7']
#     parama_params = [
#         [news, start_list[6], end_list[6], files_list[0]],
#         [news, start_list[1], end_list[1], files_list[1]],
#         [news, start_list[2], end_list[2], files_list[2]],
#         [news, start_list[3], end_list[3], files_list[3]],
#         [news, start_list[4], end_list[4], files_list[4]],
#         [news, start_list[5], end_list[5], files_list[5]],
#         [news, start_list[6], end_list[6], files_list[6]],
#     ]
#
#     def parse_plz(params: list):
#         news = params[0]
#         start = params[1]
#         end = params[2]
#         file_name = params[3]
#         write_file = open('newsTexts/{}.txt'.format(file_name), 'w')
#         path_to_tomita = '/home/pok/sem/parsers/tomita{}/tomita-parser/build/bin'.format(file_name[6])
#         for i in trange(start, end, file=sys.stdout, desc='outer loop'):
#             current_text = news[i]
#             command = 'echo "{0}" | {1}/tomita-parser {1}/config{2}.proto'.format(current_text, path_to_tomita,
#                                                                                   file_name[6])
#             p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
#             p.wait()
#
#             read_file = open('./TomitaOut/facts{}.txt'.format(file_name[6]), 'r')
#             tomita_data = read_file.read()
#             if 'Name = ' in tomita_data:
#                 write_file.write(tomita_data + delimiter)
#             read_file.close()
#         write_file.close()
#
#     parse_plz(parama_params[int(i)])
# work(i)