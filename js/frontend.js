/*
这个文件主要写的是将生成的代码发送到后台用到的函数
*/
//用户输入
var rawInputLst = [];

function executeCodeFromBlockly() {
  rawInputLst = []; //此时是点击python选项卡引发的执行，没有用户输入
  executeCode();
}

function executeCodeWithRawInput(rawInputStr, curInstr) {
  rawInputLst.push(rawInputStr);
  console.log('executeCodeWithRawInput', rawInputStr, curInstr, rawInputLst);
  executeCode(curInstr);
}

function setFronendError(lines) {
  $("#frontendErrorOutput").html(lines.map(htmlspecialchars).join('<br/>'));
}

//更新页面内容
function updateAppDisplay() {
    myVisualizer.updateOutput();
    $(document).scrollTop(0); // 页面定位到最上方

}

function executeCode(forceStartingInstr, forceRawInputLst) {
  if (forceRawInputLst !== undefined) {
    rawInputLst = forceRawInputLst; 
  }
  //后端运行脚本
  var backend_script = 'exec';
  //为了在遇到用户输入时继续执行的情况
  var startingInstruction = forceStartingInstr ? forceStartingInstr : 0;  
  var frontendOptionsObj = getBaseFrontendOptionsObj();
  frontendOptionsObj.startingInstruction = startingInstruction;

  executeCodeAndCreateViz(script,
                          backend_script,
                          frontendOptionsObj,
                          'content_python',
						  //处理成功后执行的函数
                          updateAppDisplay);
}

function getBaseFrontendOptionsObj() {
  var ret = {
              executeCodeWithRawInputFunc: executeCodeWithRawInput,
            };
  return ret;
}

function executeCodeAndCreateViz(codeToExec,
                                 backendScript,
                                 frontendOptionsObj,
                                 outputDiv,
                                 handleSuccessFunc) {

    //回调函数
	function execCallback(dataFromBackend) {
      //获取后端发回的数据
	  var trace = dataFromBackend.trace;

      var killerException = null;

      // 如果返回的数据有错误，不要进入可视化模式
      if (!trace ||
          (trace.length == 0) ||
          (trace[trace.length - 1].event == 'uncaught_exception')) {

        if (trace.length == 1) {
          killerException = trace[0]; 
          setFronendError([trace[0].exception_msg]);
        }
        else if (trace.length > 0 && trace[trace.length - 1].exception_msg) {
          killerException = trace[trace.length - 1]; 
          setFronendError([trace[trace.length - 1].exception_msg]);
        }
        else {
          setFronendError(["Unknown error"]);
        }
      }
      else {
        //防止指令执行发生越界
        if (frontendOptionsObj.startingInstruction >= trace.length) {
          frontendOptionsObj.startingInstruction = 0;
        }
        //新建可视化实例
        myVisualizer = new ExecutionVisualizer(outputDiv, dataFromBackend, frontendOptionsObj);
        //处理成功，调用可视化函数updateAppDisplay
        handleSuccessFunc();
      }

    }
	//发送数据到后端
    $.get(backendScript,
            {user_script : codeToExec,
             raw_input_json: rawInputLst.length > 0 ? JSON.stringify(rawInputLst) : ''},
             execCallback, "json");

}