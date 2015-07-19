### adt安装
在http://developer.android.com/sdk/index.html下载包。由于本人机器上安装的是64位的debian系统，因此下载好解压开来执行时会有问题，会报如下错误：
	
	Unexpected exception ‘Cannot run program “/home/android/sdk/platform-tools/adb”: java.io.IOException: error=2, No such file or directory’ while attempting to get adb version from ‘/home/android/sdk/platform-tools/adb’
出现上面的问题主要原因是adb是32位的，而我的系统是64位的，需要安装ia32-libs这个库来：
	
	apt-get install ia32-libs

这时又出现了一个问题：
	
	ia32-libs : 依赖: ia32-libs-i386 但无法安装它

即使使用`apt-get -f install`也无法解决，后来查了一下，需要加入一包：
	
	sudo dpkg --add-architecture i386  
	sudo apt-get update  

执行完上面之后再去安装就可以安装成功。
安装成功后再去执行adb，又出现了另外一个问题：
	
	./adb: error while loading shared libraries: libncurses.so.5
需要安装另外一个包才行：
	
	sudo apt-get install libncurses5:i386
至此全部安装成功！

### android studio安装
android studio的安装出现了一个问题，启动程序时过加进度条后会报一个错误：  
	
	Plug com.intellij failed to initialize and will be disabled:null  
网上给出两种解决方案：  
    

* 安装自带jdk
	
		sudo apt-get install openjdk-6-jdk
* 将建立/opt/java的软链接至java_home
		
		sudo ln -s $JAVA_HOME /opt/java  
    

再启动则可以进行android studio