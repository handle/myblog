title: java并发之CountDownLatch、Semaphore和CyclicBarrier
date: 2013-06-03 12:00
category: Java
tags: 沧海拾遗

JAVA并发包中有三个类用于同步一批线程的行为，分别是CountDownLatch、Semaphore和CyclicBarrier。
### CountDownLatch
CountDownLatch是一个计数器闭锁，主要的功能就是通过await()方法来阻塞住当前线程，然后等待计数器减少到0了，再唤起这些线程继续执行。
这个类里主要有两个方法，一个是向下减计数器的方法:countdown(),其实现的核心代码如下:

	public boolean tryReleaseShared(int releases) {
		// Decrement count; signal when transition to zero
		for (;;) {
		int c = getState();
		if (c == 0)
			return false;
		int nextc = c-1;
		if (compareAndSetState(c, nextc))
			return nextc == 0;
		}
	}

很简单，如果取得当前的状态为0,说明这个锁已经结束，直接返回false;如果没有结束，然后去设置计数器减1,如果compareAndSetState不成功，则继续循环执行。
而其中的一直等待计数器归零的方法是await()。
通过CountDownLatch可以做几件事情：

1.  主线程控制同时启动一组线程

		final CountDownLatch count = new CountDownLatch(1);
    	for (int i = 0; i < 3; i++) {
        	new Thread("Thread" + i) {
            	public void run() {
                	System.out.println(Thread.currentThread().getName() + " wait");
                	try {
                    	count.await();
                	} catch (InterruptedException e) {
                    	e.printStackTrace();
                	}
                	System.out.println(Thread.currentThread().getName() + " start");
            	}
        	}.start();
    	}
    	//等等三秒，否则有可能3个线程并没有全部进行await状态
    	try {
        	Thread.sleep(3000);
    	} catch (InterruptedException e) {
        	e.printStackTrace();
    	}
    	count.countDown();

2.  主线程等待各子线程全部执行完毕后再往下执行:

    	final CountDownLatch count = new CountDownLatch(3);
    	for (int i = 0; i < 3; i++) {
        	new Thread("Thread" + i) {
            	public void run() {
                	System.out.println(Thread.currentThread().getName() + " start");
                	count.countDown();
            	}
        	}.start();
    	}
    	try {
        	count.await();
    	} catch (InterruptedException e) {
        	e.printStackTrace();
    	}
    	System.out.println("All end!!!");

### Semaphore
Semaphore与CountDownLatch相似，不同的地方在于Semaphore的值被获取到后是可以释放的，并不像CountDownLatch那样一直减到底。它也被更多地用来限制流量，类似阀门的
功能。如果限定某些资源最多有N个线程可以访问，那么超过N个主不允许再有线程来访问，同时当现有线程结束后，就会释放，然后允许新的线程进来。有点类似于锁的lock与
unlock过程。相对来说他也有两个主要的方法：
1. 用于获取权限的acquire(),其底层实现与CountDownLatch.countdown()类似;
2. 用于释放权限的release()，其底层实现与acquire()是一个互逆的过程。


用Semaphore来实现限流代码详见：[semaphore例子](https://github.com/handle/resourcelimitor/blob/master/ResourceLimitor.java   )

### CyclicBarrier
CyclicBarrier是用来一个关卡来阻挡住所有线程，等所有线程全部执行到关卡处时，再统一执行下一步操作，它里面最重要的方法是await()方法，其实现如下：

    private int dowait(boolean timed, long nanos)
        throws InterruptedException, BrokenBarrierException,
               TimeoutException {
        //取锁，以防止在后面做减1计数时线程不安全
        final ReentrantLock lock = this.lock;
        lock.lock();
        try {
            final Generation g = generation;

            if (g.broken)
                throw new BrokenBarrierException();

            if (Thread.interrupted()) {
                breakBarrier();
                throw new InterruptedException();
            }
           //如果当前线程执行到了，则将计数器减1,计数器为0则说明所有线程均执行到这里，可以调用下一步操作
           int index = --count;
           if (index == 0) {  // tripped
               boolean ranAction = false;
               try {
                   //获取到定义好的下一步操作,并执行
		   final Runnable command = barrierCommand;
                   if (command != null)
                       command.run();
                   ranAction = true;
                   nextGeneration();
                   return 0;
               } finally {
                   if (!ranAction)
                       breakBarrier();
               }
           }

            // loop until tripped, broken, interrupted, or timed out
            for (;;) {
                try {
                    if (!timed)
                        trip.await();
                    else if (nanos > 0L)
                        nanos = trip.awaitNanos(nanos);
                } catch (InterruptedException ie) {
                    if (g == generation && ! g.broken) {
                        breakBarrier();
			throw ie;
		    } else {
			// We're about to finish waiting even if we had not
			// been interrupted, so this interrupt is deemed to
			// "belong" to subsequent execution.
			Thread.currentThread().interrupt();
		    }
                }

                if (g.broken)
                    throw new BrokenBarrierException();

                if (g != generation)
                    return index;

                if (timed && nanos <= 0L) {
                    breakBarrier();
                    throw new TimeoutException();
                }
            }
        } finally {
            lock.unlock();
        }
    }

即每个线程执行完后调用await(),然后在await()里，线程先将计数器减1,如果计数器为0，则执行定义好的操作，然后再继续执行原线程的内容。
这个类比之前两个类的一个好处是有点类似于切面编程，可以让我们在同类线程的某个切面切入一块逻辑，并且可以同步所有的线程的执行速度。
例子代码如下：

    final CyclicBarrier barrier = new CyclicBarrier(4, new Runnable() {

        @Override
        public void run() {
            System.out.println("All Threads Here");

        }
    });
    for (int i = 0; i < 4; i++) {
        new Thread("Thread" + i) {
            public void run() {
                System.out.println(Thread.currentThread().getName() + " wait");
                try {
                    barrier.await();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                } catch (BrokenBarrierException e) {
                    e.printStackTrace();
                }
                System.out.println(Thread.currentThread().getName() + " crossed");
            }
        }.start();
    }

最终的输出结果为：

    Thread0 wait
    Thread1 wait
    Thread2 wait
    Thread3 wait
    All Threads Here
    Thread0 crossed
    Thread1 crossed
    Thread2 crossed
    Thread3 crossed
