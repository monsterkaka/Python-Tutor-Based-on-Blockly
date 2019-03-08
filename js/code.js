 //严格模式
'use strict';

//创建命名空间
var Code = {};

var script = '';

Code.workspace = null;

//存储已经编写的程序
Code.loadBlocks = function(defaultXml) {
  try {
    var loadOnce = window.sessionStorage.loadOnceBlocks;
  } catch(e) {
    var loadOnce = null;
  }
  if (loadOnce) {
    // 语言切换时存储已经编写的程序
    delete window.sessionStorage.loadOnceBlocks;
    var xml = Blockly.Xml.textToDom(loadOnce);
    Blockly.Xml.domToWorkspace(xml, Code.workspace);
  } else if (defaultXml) {
    //将默认的开始块（xml数据）填充到编辑器中
    var xml = Blockly.Xml.textToDom(defaultXml);
    Blockly.Xml.domToWorkspace(xml, Code.workspace);
  }
};

//绑定点击和触摸事件到按钮
Code.bindClick = function(el, func) {
  if (typeof el == 'string') {
    el = document.getElementById(el);
  }
  el.addEventListener('click', func, true);
  el.addEventListener('touchend', func, true);
};

//获取绝对位置和坐标
Code.getBBox_ = function(element) {
  var height = element.offsetHeight;
  var width = element.offsetWidth;
  var x = 0;
  var y = 0;
  do {
    x += element.offsetLeft;
    y += element.offsetTop;
    element = element.offsetParent;//获取离他最近的元素
  } while (element);
  return {
    height: height,
    width: width,
    x: x,
    y: y
  };
};

//语言
//Code.LANG = Code.getLang();
Code.LANG = 'zh-hans'
//选项卡列表和默认选中
Code.TABS_ = ['blocks', 'python'];
Code.selected = 'blocks';

//当选项卡被点击切换可见的面板
Code.tabClick = function(clickedName) {

  //如果当前blocks选项卡是选中状态，隐藏工作区
  if (document.getElementById('tab_blocks').className == 'tabon') {
    Code.workspace.setVisible(false);
  }
  // 取消选中所有选项卡并隐藏所有面板
  for (var i = 0; i < Code.TABS_.length; i++) {
    var name = Code.TABS_[i];
    document.getElementById('tab_' + name).className = 'taboff';
    document.getElementById('content_' + name).style.visibility = 'hidden';
  }

  // 选中被点击的选项卡
  Code.selected = clickedName;
  document.getElementById('tab_' + clickedName).className = 'tabon';
  // 显示被选中的面板
  document.getElementById('content_' + clickedName).style.visibility =
      'visible';
  //渲染面板内容
  Code.renderContent();
  //如果被选中的是blocks，显示工作区
  if (clickedName == 'blocks') {
    Code.workspace.setVisible(true);
  }
  //编辑界面的元素是svg格式
  Blockly.svgResize(Code.workspace);
};

//用相应程序渲染相应的面板内容
Code.renderContent = function() {
  var content = document.getElementById('content_' + Code.selected);
  // 初始化面板
  if (content.id == 'content_python') {
    Code.attemptCodeGeneration(Blockly.Python, 'py');
  }
};

//产生并显示相应代码
Code.attemptCodeGeneration = function(generator, prettyPrintType) {
  var content = document.getElementById('content_' + Code.selected);
  content.textContent = '';
  if (Code.checkAllGeneratorFunctionsDefined(generator)) {
    script = generator.workspaceToCode(Code.workspace);
    executeCodeFromBlockly();
    //content.textContent = code;
  }
};

//检查相应语言的每种块的代码产生规则是否存在
Code.checkAllGeneratorFunctionsDefined = function(generator) {
  var blocks = Code.workspace.getAllBlocks(false);
  var missingBlockGenerators = [];
  for (var i = 0; i < blocks.length; i++) {
    var blockType = blocks[i].type;
    if (!generator[blockType]) {
      if (missingBlockGenerators.indexOf(blockType) === -1) {
        missingBlockGenerators.push(blockType);
      }
    }
  }

  var valid = missingBlockGenerators.length == 0;
  if (!valid) {
    var msg = 'The generator code for the following blocks not specified for '
        + generator.name_ + ':\n - ' + missingBlockGenerators.join('\n - ');
    Blockly.alert(msg);  
  }
  return valid;
};

//当页面被加载时，初始化blockly
Code.init = function() {

  //获取编辑区实例
  var container = document.getElementById('content_area');
  //定义页面自动放缩
  var onresize = function(e) {
    var bBox = Code.getBBox_(container);
    for (var i = 0; i < Code.TABS_.length; i++) {
      var el = document.getElementById('content_' + Code.TABS_[i]);
      el.style.top = bBox.y + 'px';
      el.style.left = bBox.x + 'px';
      el.style.height = bBox.height + 'px';
      el.style.height = (2 * bBox.height - el.offsetHeight) + 'px';
      el.style.width = bBox.width + 'px';
      el.style.width = (2 * bBox.width - el.offsetWidth) + 'px';
    }
    if (Code.workspace && Code.workspace.toolbox_.width) {
      document.getElementById('tab_blocks').style.minWidth =
          (Code.workspace.toolbox_.width - 38) + 'px';
    }
  };
  //当页面大小改变，调用页面缩放函数
  window.addEventListener('resize', onresize, false);

  //取出代号对应的中文，之所以如此是为了方便以后支持其他语言
  for (var messageKey in MSG) {
    if (messageKey.indexOf('cat') == 0) {
      Blockly.Msg[messageKey.toUpperCase()] = MSG[messageKey];
    }
  }

  //将工具箱中代码块用到的代号替换成中文
  var toolboxText = document.getElementById('toolbox').outerHTML;
  toolboxText = toolboxText.replace(/(^|[^%]){(\w+)}/g,
      function(m, p1, p2) {return p1 + MSG[p2];});
  var toolboxXml = Blockly.Xml.textToDom(toolboxText);
  //在页面中插入blockly编辑器
  Code.workspace = Blockly.inject('content_blocks',
      {grid:
          {spacing: 25,
           length: 3,
           colour: '#ccc',
           snap: true},
       media: 'media/',
       toolbox: toolboxXml,
       zoom:
           {controls: true,
            wheel: true}
      });
  //预加载示例程序   
  //Code.loadBlocks('');
  Code.loadBlocks(example);
  //切换到被选中的面板，默认是blockly编辑面板
  Code.tabClick(Code.selected);
  //给选项卡绑定点击和触摸事件，当事件发生触发相应的函数
  for (var i = 0; i < Code.TABS_.length; i++) {
    var name = Code.TABS_[i];
    Code.bindClick('tab_' + name,
        function(name_) {return function() {Code.tabClick(name_);};}(name));
  }
  //调整工作区以正确显示
  onresize();
  Blockly.svgResize(Code.workspace);

};

// 加载示例界面的语言字符串
document.write('<script src="msg/' + Code.LANG + '-fronted.js"></script>\n');
// 加载blockly自带的语言字符串
document.write('<script src="msg/' + Code.LANG + '-blockly.js"></script>\n');
// 当页面被加载，初始化页面
window.addEventListener('load', Code.init);
