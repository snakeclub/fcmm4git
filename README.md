# fcmm4git
fcmm4git（FCMM for Git）是基于FCMM模型，针对git简化进行代码托管的一个命令行小工具，基础版本正在开发中……



## 安装及配置



### fcmm.json

fcmm.json是fcmm4git的工具配置文件，定义了工具的一些信息，可以通过修改该配置文件达到一些个性化的需求，配置文件的内容说明如下：

    "consle_encode": "GBK"  -  控制台的语言编码，对于windows平台应设置为GBK，避免命令返回信息乱码

    "temp_path": "temp/"  -  进行处理需要比对文件的临时目录

    "backup_before": "true"  -  是否在初始化前进行备份，将本地目录备份到temp_path指定的位置；对于远程仓库的情况，会将远程仓库下载下来然后备份到备份目录中

    "backup_path": "backup/"  -  本地目录备份的目录

    "tips"   -   工具进入命令交互模式时的提示信息

    "cmd_para"   -   支持的命令交互命令清单配置（含自动完成提示）；如果想控制某些命令不允许执行，可以删除相应命令的配置

    "help_text"   -  工具命令的帮助信息，可以通过修改配置改变提示信息（例如改变语言来支持多语言）

    "i18n_tips"   -  多语言提示信息内容，可以通过修改配置改变提示信息语言



### .fcmm4git 

每一个建立了FCMM的库都会在根目录下有一个.fcmm4git 文件，该文件用于登记相应库的fcmm4git配置信息。该文件实际上是一个json文件，内容说明如下：





## 命令说明

### 初始化FCMM版本库（init）

说明：根据指定的参数建立及初始化FCMM版本库

外部命令：fcmm init [参数……]

内部命令：init [参数……]

参数定义（有长参数和短参数两种形式）：

	-help / -h : 获取命令帮助信息

	-base / -b : 参数值local/remote，指定初始化的原始版本基于本地还是远程，无论基于本地还是远程，都会判断另一端是否有版本或文件的存在，如果有则报错不处理

	-force / -f ：指定是否强制初始化，如果指定强制初始化，另一端的文件和版本会被清除覆盖掉，因此force参数要慎用

	-reset / -r :  仅针对local模式，指定是否重置服务器端的历史，如果指定该参数，将会使用本地的git信息覆盖服务器；不指定参数会删除远端服务器的所有文件，并使用本地文件重置

	-url / -u : 指定远程git服务的url，例如“https://github.com/snakeclub/fcmm4git.git”

	-version / -v : 指定当前版本库的版本，例如“v1.0.1”或“d20180620-1”

	-nopkg / -n : 指定不建立lb-pkg分支，不指定该参数则会建立该分支



## 新增FCMM分支(add)

### 新增pkg分支

说明：新增FCMM的pkg分支，如果原分支存在，可以重置分支

外部命令：fcmm add-pkg [参数……]

内部命令：add-pkg [参数……]

参数定义（有长参数和短参数两种形式）根据：

	-help / -h : 获取命令帮助信息

	-version / -v : 指定新增分支获取的master版本库的版本，如果不设置默认取master最新的版本

	-force / -f ：指定强制创建，如不指定，当分支已存在不会执行处理

### 新增配置分支

说明：新增FCMM的配置分支，如果原分支存在，可以重置分支

外部命令：fcmm add-cfg [参数……]

内部命令：add-cfg [参数……]

参数定义（有长参数和短参数两种形式）根据：

	-help / -h : 获取命令帮助信息

	-name / -n : 要创建的配置分支的标识名，例如uat

	-bare / -b : 标识要创建的分支是空白分支

	-clone / -c : 从其他配置分支复制，参数值为其他配置分支的标识名，例如sit

	-force / -f ：指定是否强制创建，如不指定，当分支已存在不会执行处理

### 新增开发分支

说明：新增FCMM的开发分支，如果原分支存在，可以重置分支

外部命令：fcmm add-dev [参数……]

内部命令：add-dev [参数……]

参数定义（有长参数和短参数两种形式）根据：

	-help / -h : 获取命令帮助信息

	-name / -n : 要创建的开发分支的标识名，例如xq2018063701

	-type / -t : 指定要创建的分支类型，参数值为req/fix/feat

	-clone / -c : 从其他开发分支复制，参数值为其他开发分支的"类型-标识名"，例如req-xq2018063701

	-version / -v : 指从master/lb-pkg的指定版本重新创建（忽略-clone参数 ）

	-tag :  获取的是指定的commit标签的版本

	-force / -f ：指定强制创建，如不指定，当分支已存在不会执行处理

### 新增开发者临时分支

说明：新增FCMM的开发者分支，如果原分支存在，可以重置分支

外部命令：fcmm add-temp [参数……]

内部命令：add-temp [参数……]

参数定义（有长参数和短参数两种形式）根据：

	-help / -h : 获取命令帮助信息

	-name / -n : 开发者名称，如果不设置则默认从git config中获取

	-bare / -b : 标识要创建的分支是空白分支，如果不指定该参数，将基于本地仓库的当前版本创建

	-force / -f ：指定强制创建，如不指定，当分支已存在不会执行处理

## 测试管理

### 绑定测试分支的配置分支

说明：绑定指定的测试分支要使用的配置分支信息；该命令会在.fcmm文件中增加测试分支与配置分支的绑定关系，也可自行设置master分支的该配置，然后同步到所有分支上

外部命令：fcmm set-testcfg [参数……]

内部命令：set-testcfg [参数……]

参数定义（有长参数和短参数两种形式）根据：

	-help / -h : 获取命令帮助信息

	-name / -n : 测试分支的标识名

	-see / -s : 查看对应的配置

	-cfg / -c : 配置分支的标识名；如果不设置该参数，则代表清空配置

	-version / -v : 绑定配置分支的指定版本，如果不设置该参数，则默认获取配置分支的最新版本

### 设置测试分支提交顺序

说明：设置测试分支的提交顺序，在顺序表中列出的测试分支，将限制只能逐级提交；该命令会在.fcmm文件中增加测试分支顺序清单的配置，也可自行设置master分支的该配置，然后同步到所有分支上

外部命令：fcmm set-testorder [参数……]

内部命令：set-testorder [参数……]

参数定义（有长参数和短参数两种形式）根据：

	-help / -h : 获取命令帮助信息

	-see / -s : 查看对应的配置

	-id / -i : 要设置的测试分支的id标识，通过不同的id标识可以设置多组顺序

	-order / -o : 测试分支标识顺序清单，通过","分隔，例如"sit,uat,qprd"；如果不设置该参数，则代表清空提交顺序

### 提交测试分支

说明：将版本提交至指定的测试分支，如果测试分支有绑定配置，则会生成对应的发布分支

外部命令：fcmm push-test[参数……]

内部命令：push-test [参数……]

参数定义（有长参数和短参数两种形式）根据：

	-help / -h : 获取命令帮助信息

	-check / -c :  提交前检查当前提交分支、测试分支、定版分支的基础版本是否一致，如果不一致则提示和中止操作；检查规则如下：

		1.测试分支的当前版本（要考虑每个文件）是否在提交分支的历史版本中（判断后面的版本是增量）；

		2.定版分支的指定版本（未指定则为最新版本）是否在提交分支的历史版本中（判断后面的版本是增量）

	-dest / -d : 目标测试分支的标识名，例如sit

	-source / -s : 当前分支标识，不指定则代表获取当前工作分支；如果是开发分支，标识应为"类型-标识"，例如req-xq2018063701；如果是测试分支，则只提供环境标识，例如uat

	-tag / -t :  指定获取source的指定commit标签的版本

	-version / -v : 指定check要比对定版分支（或master）的版本

	-reset / -r : 指定重置测试分支（采用清空覆盖的方式），该参数要与force参数一并使用

	-force / -f ：指定强制提交，如不指定，在测试分支提交顺序校验不通过的时候，将中止处理

### 重建发布分支

说明：重新建立发布分支（测试分支存在的情况下）

外部命令：fcmm reset-pub [参数……]

内部命令：reset-pub [参数……]

参数定义（有长参数和短参数两种形式）根据：

	-help / -h : 获取命令帮助信息

	-name / -n : 测试分支的标识名

	-tag / -t :  指定获取测试分支i的指定commit标签的版本

	-force / -f ：指定强制提交，如不指定在发布分支存在的情况下提示并中止

## 定版及投产

### 绑定定版配置

说明：绑定定版的配置文件和可提交的测试分支（注意如果配置中没有建立定版分支，实际上直接绑定到master上）

外部命令：fcmm set-pkgcfg [参数……]

内部命令：set-pkgcfg [参数……]

参数定义（有长参数和短参数两种形式）根据：

	-help / -h : 获取命令帮助信息

	-name / -n : 要绑定的测试分支的标识名清单，用","分隔，可以绑定多个测试分支

	-see / -s : 查看对应的配置

	-cfg / -c : 配置分支的标识名；如果不设置该参数，则代表清空配置

	-version / -v : 绑定配置分支的指定版本，如果不设置该参数，则默认获取配置分支的最新版本

### 提交定版

说明：从测试环境提交版本至定版分支（注意如果配置中没有建立定版分支，实际上直接提交到master上）

外部命令：fcmm push-pkg [参数……]

内部命令：push-pkg [参数……]

参数定义（有长参数和短参数两种形式）根据：

	-help / -h : 获取命令帮助信息

	-check / -c :  提交前检查当前测试分支、定版分支的基础版本是否一致，如果不一致则提示和中止操作

	-name / -n :  要获取的测试分支的标识，例如sit；如不指定则获取当前本地工作分支

	-version / -v : 指定定版的版本号

	-tag / -t :  指定获取测试分支i的指定commit标签的版本，该参数必须与force参数共同使用

	-force / -f ：指定强制提交，如指定后检查不过以及非绑定测试分支也允许提交

### 投产确认

说明：投产后，将定版分支中的指定版本提交到master版本（注意如果配置中没有建立定版分支，该操作无效）

外部命令：fcmm push-master [参数……]

内部命令：push-master [参数……]

参数定义（有长参数和短参数两种形式）根据：

	-help / -h : 获取命令帮助信息

	-check / -c :  提交前检查定版分支、master的基础版本是否一致，如果不一致则提示和中止操作

	-version / -v : 指定定版分支的版本号

	-newversion / -nv : 变更master的版本号，设置一个新版本号

## 其他管理

### 回退分支版本

说明：将指定分支回退到指定版本

外部命令：fcmm rollback [参数……]

内部命令：rollback [参数……]

参数定义（有长参数和短参数两种形式）根据：

	-help / -h : 获取命令帮助信息

	-name / -n : 分支完整标识，例如master，lb-pkg；如果不传入代表回退当前工作分支

	-version / -v : 要回退到的版本号

	-tag / -t :  要回退到的commit标签的版本，该参数与version 参数互斥

	-force / -f ：指定强制提交，如不指定，master和定版分支不允许回退

### 检查分支基础版本

说明：检查分支的基础版本与指定分支是否一致（比较版本在检查分支的历史节点里）

外部命令：fcmm check [参数……]

内部命令：check [参数……]

参数定义（有长参数和短参数两种形式）根据：

	-help / -h : 获取命令帮助信息

	-name / -n : 检查分支完整标识，例如master，lb-pkg；如果不传入代表当前工作分支

	-source / -s : 指定要比较分支的完整标识，例如master，lb-pkg；如果不传入代表master，lb-pkg分支

	-version / -v : 要比较分支的指定版本号；与tag参数互斥

	-tag / -t :  要比较分支的指定commit标签，该参数与version 参数互斥，如果不指定，则为分支的最新提交

### 合并分支

说明：将指定分支版本合并到当前分支中

外部命令：fcmm merge [参数……]

内部命令：merge [参数……]

参数定义（有长参数和短参数两种形式）根据：

	-help / -h : 获取命令帮助信息

	-dest / -d : 目标分支完整标识，例如master，lb-pkg；如果不传入代表当前工作分支

	-source / -s : 指定要合并的源分支的完整标识，例如master，lb-pkg

	-version / -v : 要合并的源分支的版本号

	-tag / -t :  要合并的源分支的的commit标签的版本，该参数与version 参数互

	-force / -f ：指定强制提交，如不指定，master和定版分支不允许合并

### 删除分支



### 缓存分支至开发者临时分支



### 从开发者临时分支创建分支







## 开源项目贡献

本项目为开源项目，基于MIT许可，欢迎大家通过Github一起对FCMM模型继续补充和完善，贡献代码的方法可参考[《开源项目贡献流程》](/docs/open-source-project-contribution-process.md)。

对于FCMM存在的问题或建议，可进入Github的[Issues](https://github.com/snakeclub/FCMM/issues)进行反馈，我将尽快修复和答复。