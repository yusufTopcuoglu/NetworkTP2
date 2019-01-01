import os

# source.py  to s
os.system("scp -P 25446 /home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/input.txt "
          " e2099398@pc2.instageni.wisc.edu:~/")

# destination.py  to d
os.system("scp -P 25443 /home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/destination.py "
          " e2099398@pc2.instageni.wisc.edu:~/")

# broker.py  to b
os.system("scp -P 25442 /home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/broker.py "
          " e2099398@pc2.instageni.wisc.edu:~/")

# from destination
os.system("scp -P 25443 e2099398@pc2.instageni.wisc.edu:~/ip_r.txt "
          "/home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/destination/")

os.system("scp -P 25443 e2099398@pc2.instageni.wisc.edu:~/ip_r_after.txt "
          "/home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/destination/")

os.system("scp -P 25443 e2099398@pc2.instageni.wisc.edu:~/route.txt "
          "/home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/destination/")

os.system("scp -P 25443 e2099398@pc2.instageni.wisc.edu:~/route_after.txt "
          "/home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/destination/")

os.system("scp -P 25443 e2099398@pc2.instageni.wisc.edu:~/traceroute_10.10.2.1.txt "
          "/home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/destination/")

os.system("scp -P 25443 e2099398@pc2.instageni.wisc.edu:~/traceroute_10.10.4.1.txt "
          "/home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/destination/")


# from broker
os.system("scp -P 25442 e2099398@pc2.instageni.wisc.edu:~/ip_r.txt "
          "/home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/broker/")

os.system("scp -P 25442 e2099398@pc2.instageni.wisc.edu:~/ip_r_after.txt "
          "/home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/broker/")

os.system("scp -P 25442 e2099398@pc2.instageni.wisc.edu:~/route.txt "
          "/home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/broker/")

os.system("scp -P 25442 e2099398@pc2.instageni.wisc.edu:~/route_after.txt "
          "/home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/broker/")

os.system("scp -P 25442 e2099398@pc2.instageni.wisc.edu:~/traceroute_10.10.5.2.txt "
          "/home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/broker/")

os.system("scp -P 25442 e2099398@pc2.instageni.wisc.edu:~/traceroute_10.10.3.2.txt "
          "/home/yuzarsif/Desktop/Dersler/Network/TermProject/Part2/NetworkTP2/broker/")
