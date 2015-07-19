title: debian安装无线网络设置
date: 2013-05-14 12:00
category: 系统网络
category: Linux
tags: 举重若轻

debain的网络设置不像ubuntu一样，会由系统来自动设置，需要我们手工配置配置文件，来进行连接。debian中的网络配置方法如下(以无线网络为例，无线网络id为wlan0)：
#### 编辑/etc/network/interface,加入如下内容：####

    auto wlan0  
    iface wlan0 inet dhcp  
        wpa-conf /etc/wpa_supplicant/wireless.conf  

#### 创建/etc/wpa_supplicant/wireless.conf文件，添加如下内容：
* wpa 企业版  
<pre>
ctrl_interface=/var/run/wpa_supplicant  
network={  
    ssid="essid"  
    scan_ssid=1  
    key_mgmt=WPA-EAP IEEE8021X  
    pairwise=CCMP  
    group=CCMP  
    eap=PEAP  
    eapol_flags=0  
    identity="XXXXXX"  
    password="XXXXXX"  
    phase1="peaplabel=0"  
    phase2="auth=MSCHAPV2"  
}
</pre>  
* wpa psrson版  
执行`wpa_passphrase essid`后会显示需要输入密码  
输入密码后就可以得到配置文件内容  
将配置内容复制到一个文件中，如/etc/wpa_supplicant/wireless.conf  
    

#### 重启网络服务  
	/etc/init.d/networking restart  
#### 问题解决  
如果通过以上步骤未能成功连上网络，则可以通过以下方法来进行方式：  
	
	killall -9 wpa_supplicant  
	ifconfig wlan0 down  
	iwconfig wlan0 mode Managed  
	ifconfig wlan0 up  
	wpa_supplicant -B -dwext -iwlan0 -c /etc/wpa_supplicant/wireless.conf -dd  
通过以上几步就能看到出错的原因。  
