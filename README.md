使用说明
	使用mysql数据库，
	初始化数据库
	python3 manage.py makemigrations
	python3 manage.py migrate
	
	创建一个管理员账号
	python3 manage.py createsuperuser 使用这个命令创建一个管理员账号。
	
	登录管理员账号，访问页面，http://127.0.0.1:8000/king_admin/crm/menu/
	添加菜单
	参照菜单图

	访问http://127.0.0.1:8000/king_admin/crm/role/
	创建3个角色，分别是学生老师和顾问
	给每个角色分配对应的url
	
	访问http://127.0.0.1:8000/king_admin/crm/userprofile/
	给顾问老师和报名的学生创建一个账户，并关联到对应的角色，并分配给他们相应的权限
	学员要关联学员账号
	
	配置好了就可以开始业务流程了。
	
	
	程序的目录：
	untitled9
		crm                客户关系管理的app
			permissions     用户权限配置及实现
		enrolled_data 	    学员报名提交的身份证所在目录
		homeworks          学员提交的作业
		king_admin         配置管理表的APP
		static             静态的网页资源文件
		student            学员的app
		templates          网页模版目录
		untitle9           项目主目录及一些配置
	

	



#crm
