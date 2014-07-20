# gist-it-sae 将GitHub源码文件嵌入到网页中

An AppEngine app to embed files from a github repository like a gist

http://github.com/pingjiang/gist-it-sae

## 在线使用方法

国内SAE云计算平台上的主页 [http://gistit.sinaapp.com/](http://gistit.sinaapp.com/)

国外Google云平台上的主页 [gist-it.appspot.com](http://gist-it.appspot.com)

## 本地使用方法

在源码根目录执行：

	dev_server.py .
	
## 代码原理

* 用户通过将自己需要嵌入的文件的URL的`https://github.com/`后的部分作为请求参数附加到`http://gistit.sinaapp.com/github`。
* 代码自动获取了用户需要嵌入的文件的GitHub的路径`https://github.com/robertkrimen/gist-it-example/raw/master/example.js`。
* 通过`urlfetch`获取源码文件。
* 将源码文件使用`Jinja2`模板格式化为最终展示的样式。
* 用户可以通过`slice`和`footer`等参数控制显示的样式，详情请参见[项目主页](http://gistit.sinaapp.com)。

## 作者

移植到SAE云平台的作者： ping jiang (pingjiang1989@gmail.com)

* [我的GitHub主页](http://github.com/pingjiang)
* [项目主页](http://gistit.sinaapp.com)

原作者： Robert Krimen (robertkrimen@gmail.com)

* [原作者GitHub主页](http://github.com/robertkrimen)
* [原作者主页](http://search.cpan.org/~rokr/?R=D)
* [原作者项目主页](http://gist-it.appspot.com)
