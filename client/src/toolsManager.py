import os
import sys
import shutil
import json
import PyEasyUtils as EasyUtils
from glob import glob
from pathlib import Path
from typing import Union, Optional, Any
from PySide6.QtCore import QObject, Signal

##############################################################################################################################

host = None
port = None
subprocessMonitor = None


def startServer(
    filePath: str,
    logPath: str
):
    """
    """
    global host, port, subprocessMonitor
    host = "localhost"
    port = EasyUtils.findAvailablePorts((8000, 8080), host)[0]
    args = EasyUtils.mkPyFileCommand(
        filePath,
        host = host,
        port = port,
    )
    spm = EasyUtils.subprocessManager(shell = True)
    spm.create(args, env = os.environ)
    subprocessMonitor = spm.monitor(logPath)
    isServerStarted = False
    for outputLine, errorLine in subprocessMonitor:
        if f"{host}:{port}" in outputLine.decode(errors = 'ignore'):
            isServerStarted = True
        yield isServerStarted
        if isServerStarted:
            break


def sendRequest(
    reqMethod: EasyUtils.requestManager,
    protocol: str,
    host: str,
    port: int,
    pathParams: Union[str, list[str], None] = None,
    **reqParams,
):
    """
    """
    output, error = b"", b""
    payload = reqParams
    future = EasyUtils.taskAccelerationManager.ThreadPool.create(
        {EasyUtils.simpleRequest: (reqMethod, protocol, host, port, pathParams, None, None, json.dumps(payload))}
    )[0]
    for outputLine, errorLine in subprocessMonitor:
        output += outputLine
        error += errorLine
        if future.done():
            break
    return output, error

##############################################################################################################################

class Tool_AudioProcessor(QObject):
    '''
    Start audio processing
    '''
    def __init__(self):
        super().__init__()

    def processAudio(self,
        inputDir: str,
        outputFormat: Optional[str] = 'wav',
        sampleRate: Optional[Union[int, str]] = None,
        sampleWidth: Optional[Union[int, str]] = None,
        toMono: bool = False,
        denoiseAudio: bool = True,
        denoiseModelPath: str = "",
        denoiseTarget: str = '',
        sliceAudio: bool = True,
        rmsThreshold: float = -40.,
        audioLength: int = 5000,
        silentInterval: int = 300,
        hopSize: int = 10,
        silenceKept: int = 1000,
        outputRoot: str = "./",
        outputDirName: str = "",
    ):
        output, error = sendRequest(
            EasyUtils.requestManager.Get, "http", host, port, "/processAudio",
            inputDir = inputDir,
            outputFormat = outputFormat,
            sampleRate = sampleRate,
            sampleWidth = sampleWidth,
            toMono = toMono,
            denoiseAudio = denoiseAudio,
            denoiseModelPath = denoiseModelPath,
            denoiseTarget = denoiseTarget,
            sliceAudio = sliceAudio,
            rmsThreshold = rmsThreshold,
            audioLength = audioLength,
            silentInterval = silentInterval,
            hopSize = hopSize,
            silenceKept = silenceKept,
            outputRoot = outputRoot,
            outputDirName = outputDirName,
        )
        if 'error' in str(error).lower():
            error += "（详情请见终端输出信息）"
        elif 'traceback' in str(output).lower():
            error = "执行完成，但疑似中途出错\n（详情请见终端输出信息）"
        else:
            return
        raise Exception(error)

    def terminate(self):
        EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", host, port, "/terminate")


class Tool_VPR(QObject):
    '''
    Start VPR inferencing
    '''
    def __init__(self):
        super().__init__()

    def infer(self,
        stdAudioSpeaker: dict,
        audioDirInput: str,
        modelPath: str = './Models/.pth',
        modelType: str = 'Ecapa-Tdnn',
        featureMethod: str = 'melspectrogram',
        decisionThreshold: float = 0.6,
        audioDuration: float = 4.2,
        outputRoot: str = "./",
        outputDirName: str = "",
        audioSpeakersDataName: str = "AudioSpeakerData",
    ):
        output, error = sendRequest(
            EasyUtils.requestManager.Get, "http", host, port, "/vpr_infer",
            stdAudioSpeaker = stdAudioSpeaker,
            audioDirInput = audioDirInput,
            modelPath = modelPath,
            modelType = modelType,
            featureMethod = featureMethod,
            decisionThreshold = decisionThreshold,
            audioDuration = audioDuration,
            outputRoot = outputRoot,
            outputDirName = outputDirName,
            audioSpeakersDataName = audioSpeakersDataName,
        )
        if 'error' in str(error).lower():
            error += "（详情请见终端输出信息）"
        elif 'traceback' in str(output).lower():
            error = "执行完成，但疑似中途出错\n（详情请见终端输出信息）"
        else:
            return
        raise Exception(error)

    def terminate(self):
        EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", host, port, "/terminate")


class Tool_Whisper(QObject):
    '''
    Start Whisper transcribing
    '''
    def __init__(self):
        super().__init__()

    def infer(self,
        modelPath: str = './Models/.pt',
        audioDir: str = './WAV_Files',
        verbose: Any = True,
        addLanguageInfo: bool = True,
        conditionOnPreviousText: Any = False,
        fp16: Any = True,
        outputRoot: str = './',
        outputDirName: str = 'SRT_Files'
    ):
        output, error = sendRequest(
            EasyUtils.requestManager.Get, "http", host, port, "/asr_infer",
            modelPath = modelPath,
            audioDir = audioDir,
            verbose = verbose,
            addLanguageInfo = addLanguageInfo,
            conditionOnPreviousText = conditionOnPreviousText,
            fp16 = fp16,
            outputRoot = outputRoot,
            outputDirName = outputDirName,
        )
        if 'error' in str(error).lower():
            error += "（详情请见终端输出信息）"
        elif 'traceback' in str(output).lower():
            error = "执行完成，但疑似中途出错\n（详情请见终端输出信息）"
        else:
            return
        raise Exception(error)

    def terminate(self):
        EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", host, port, "/terminate")


class Tool_GPTSoVITS(QObject):
    '''
    Start GPTSoVITS preprocessing
    '''
    def __init__(self):
        super().__init__()

    def preprocess(self,
        srtDir: str,
        audioSpeakersDataPath: str,
        dataFormat: str = 'PATH|NAME|LANG|TEXT',
        outputRoot: str = "./",
        outputDirName: str = "",
        fileListName: str = 'FileList'
    ):
        output, error = sendRequest(
            EasyUtils.requestManager.Get, "http", host, port, "/gptsovits_createDataset",
            srtDir = srtDir,
            audioSpeakersDataPath = audioSpeakersDataPath,
            dataFormat = dataFormat,
            outputRoot = outputRoot,
            outputDirName = outputDirName,
            fileListName = fileListName,
        )
        if 'error' in str(error).lower():
            error += "（详情请见终端输出信息）"
        elif 'traceback' in str(output).lower():
            error = "执行完成，但疑似中途出错\n（详情请见终端输出信息）"
        else:
            return
        raise Exception(error)

    def train(self,
        version: str = "v3",
        fileList_path: str = "GPT-SoVITS/raw/xxx.list",
        modelDir_bert: str = "GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large",
        modelDir_hubert: str = "GPT_SoVITS/pretrained_models/chinese-hubert-base",
        modelPath_gpt: str = "GPT_SoVITS/pretrained_models/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt",
        modelPath_sovitsG: str = "GPT_SoVITS/pretrained_models/s2G2333k.pth",
        modelPath_sovitsD: str = "GPT_SoVITS/pretrained_models/s2D2333k.pth",
        half_precision: bool = False, # 16系卡没有半精度
        if_grad_ckpt: bool = False, # v3是否开启梯度检查点节省显存占用
        lora_rank: int = 32, # Lora秩 choices=[16, 32, 64, 128]
        output_root: str = "SoVITS_weights&GPT_weights",
        output_dirName: str = "模型名",
        output_logDir: str = "logs",
    ):
        output, error = sendRequest(
            EasyUtils.requestManager.Get, "http", host, port, "/gptsovits_train",
            version = version,
            fileList_path = fileList_path,
            modelDir_bert = modelDir_bert,
            modelDir_hubert = modelDir_hubert,
            modelPath_gpt = modelPath_gpt,
            modelPath_sovitsG = modelPath_sovitsG,
            modelPath_sovitsD = modelPath_sovitsD,
            half_precision = half_precision,
            if_grad_ckpt = if_grad_ckpt,
            lora_rank = lora_rank,
            output_root = output_root,
            output_dirName = output_dirName,
            output_logDir = output_logDir,
        )
        if 'error' in str(error).lower():
            error += "（详情请见终端输出信息）"
        elif 'traceback' in str(output).lower():
            error = "执行完成，但疑似中途出错\n（详情请见终端输出信息）"
        else:
            return
        raise Exception(error)

    def infer_webui(self,
        version: str = "v3",
        sovits_path: str = ...,
        sovits_v3_path: str = ...,
        gpt_path: str = ...,
        cnhubert_base_path: str = ...,
        bert_path: str = ...,
        bigvgan_path: str = ...,
        half_precision: bool = True,
        batched_infer: bool = False,
    ):
        output, error = sendRequest(
            EasyUtils.requestManager.Get, "http", host, port, "/gptsovits_infer_webui",
            version = version,
            sovits_path = sovits_path,
            sovits_v3_path = sovits_v3_path,
            gpt_path = gpt_path,
            cnhubert_base_path = cnhubert_base_path,
            bert_path = bert_path,
            bigvgan_path = bigvgan_path,
            half_precision = half_precision,
            batched_infer = batched_infer,
        )
        if 'error' in str(error).lower():
            error += "（详情请见终端输出信息）"
        elif 'traceback' in str(output).lower():
            error = "执行完成，但疑似中途出错\n（详情请见终端输出信息）"
        else:
            return
        raise Exception(error)

    def infer_init(self,
        sovits_path: str,
        sovits_v3_path: str,
        gpt_path: str,
        cnhubert_base_path: str,
        bert_path: str,
        bigvgan_path: str,
        refer_wav_path: str = ..., # 参考音频路径
        prompt_text: str = ..., # 参考音频文本
        prompt_language: str = 'auto', # 参考音频语言 ['zh', 'yue', 'en', 'ja', 'ko', 'auto', 'auto_yue']
        device: str = 'cuda', # 生成引擎 ['cuda', 'cpu']
        half_precision: bool = True, # 是否使用半精度
        media_type: str = 'wav', # 音频格式 ['wav', 'ogg', 'aac']
        sub_type: str = 'int16', # 数据类型 ['int16', 'int32']
        stream_mode: str = 'normal', # 流式模式 ['close', 'normal', 'keepalive']
    ):
        output, error = sendRequest(
            EasyUtils.requestManager.Get, "http", host, port, "/gptsovits_infer_init",
            sovits_path = sovits_path,
            sovits_v3_path = sovits_v3_path,
            gpt_path = gpt_path,
            cnhubert_base_path = cnhubert_base_path,
            bert_path = bert_path,
            bigvgan_path = bigvgan_path,
            refer_wav_path = refer_wav_path,
            prompt_text = prompt_text,
            prompt_language = prompt_language,
            device = device,
            half_precision = half_precision,
            media_type = media_type,
            sub_type = sub_type,
            stream_mode = stream_mode,
        )
        if 'error' in str(error).lower():
            error += "（详情请见终端输出信息）"
        elif 'traceback' in str(output).lower():
            error = "执行完成，但疑似中途出错\n（详情请见终端输出信息）"
        else:
            return
        raise Exception(error)

    def infer_handle(self,
        refer_wav_path: str = ..., # 参考音频路径
        prompt_text: str = ..., # 参考音频文本
        prompt_language: str = 'auto', # 参考音频语言 ['zh', 'yue', 'en', 'ja', 'ko', 'auto', 'auto_yue']
        inp_refs: Optional[list] = None, # 辅助参考音频路径列表
        text: str = ..., # 待合成文本
        text_language: str = 'auto', # 目标文本语言 ['zh', 'yue', 'en', 'ja', 'ko', 'auto', 'auto_yue']
        cut_punc: Optional[str] = None, # 文本切分符号 [',', '.', ';', '?', '!', '、', '，', '。', '？', '！', '；', '：', '…']
        top_k: int = 5, # Top-K 采样值
        top_p: float = 1.0, # Top-P 采样值
        temperature: float = 1.0, # 温度值
        speed: float = 1.0, # 语速因子
        sample_steps: int = 32, # 采样步数 [4, 8, 16, 32]
        if_sr: bool = False, # 是否超分
    ):
        output, error = sendRequest(
            EasyUtils.requestManager.Get, "http", host, port, "/gptsovits_infer_handle",
            refer_wav_path = refer_wav_path,
            prompt_text = prompt_text,
            prompt_language = prompt_language,
            inp_refs = inp_refs,
            text = text,
            text_language = text_language,
            cut_punc = cut_punc,
            top_k = top_k,
            top_p = top_p,
            temperature = temperature,
            speed = speed,
            sample_steps = sample_steps,
            if_sr = if_sr,
        )
        if 'error' in str(error).lower():
            error += "（详情请见终端输出信息）"
        elif 'traceback' in str(output).lower():
            error = "执行完成，但疑似中途出错\n（详情请见终端输出信息）"
        else:
            return
        raise Exception(error)

    def terminate(self):
        EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", host, port, "/terminate")

##############################################################################################################################

def VPRResult_Get(audioSpeakersData_path: str):
    """
    GetVPRResult
    """
    AudioSpeakerSimList = []
    with open(audioSpeakersData_path, mode = 'r', encoding = 'utf-8') as AudioSpeakersData:
        AudioSpeakerSimLines = AudioSpeakersData.readlines()
    for AudioSpeakerSimLine in AudioSpeakerSimLines:
        AudioSpeakerSim = AudioSpeakerSimLine.strip().split('|')
        if len(AudioSpeakerSim) == 2:
            AudioSpeakerSim.append('')
        AudioSpeakerSimList.append(AudioSpeakerSim)
    return AudioSpeakerSimList


def VPRResult_Save(audioSpeakers: dict, audioSpeakersData_path: str, moveAudio: bool, moveToDst: Optional[str] = None):
    """
    SaveVPRResult
    """
    with open(audioSpeakersData_path, mode = 'w', encoding = 'utf-8') as AudioSpeakersData:
        Lines = []
        for Audio, Speaker in audioSpeakers.items():
            Speaker = Speaker.strip()
            if Speaker == '':
                continue
            if moveAudio:
                if moveToDst is None:
                    raise Exception("Destination shouldn't be 'None'")
                MoveToDst_Sub = EasyUtils.normPath(Path(moveToDst).joinpath(Speaker))
                os.makedirs(MoveToDst_Sub, exist_ok = True) if Path(MoveToDst_Sub).exists() == False else None
                Audio_Dst = EasyUtils.normPath(Path(MoveToDst_Sub).joinpath(Path(Audio).name).as_posix())
                shutil.copy(Audio, MoveToDst_Sub) if not Path(Audio_Dst).exists() else None
                Lines.append(f"{Audio_Dst}|{Speaker}\n")
            else:
                Lines.append(f"{Audio}|{Speaker}\n")
        AudioSpeakersData.writelines(Lines)


def ASRResult_Get(srtDir: str, audioDir: str):
    """
    GetASRResult
    """
    asrResult = {}
    for SRTFile in glob(EasyUtils.normPath(Path(srtDir).joinpath('*.srt'))):
        AudioFiles = glob(EasyUtils.normPath(Path(audioDir).joinpath('**', f'{Path(SRTFile).stem}.*')), recursive = True)
        if len(AudioFiles) == 0:
            continue
        with open(SRTFile, mode = 'r', encoding = 'utf-8') as SRT:
            SRTContent = SRT.read()
        asrResult[AudioFiles[0]] = SRTContent
    return asrResult


def ASRResult_Save(asrResult: dict, srtDir: str):
    """
    SaveASRResult
    """
    for AudioFile in asrResult.keys():
        SRTFiles = glob(EasyUtils.normPath(Path(srtDir).joinpath(f'{Path(AudioFile).stem}.*')))
        if len(SRTFiles) == 0:
            continue
        with open(SRTFiles[0], mode = 'w', encoding = 'utf-8') as SRT:
            SRT.write(asrResult[AudioFile])


def DATResult_Get(datPath: str):
    """
    GetDATResult
    """
    datResult = {}
    with open(datPath, mode = 'r', encoding = 'utf-8') as DAT:
        DATLines = DAT.readlines()
    for DATLine in DATLines:
        Audio = EasyUtils.normPath(Path(datPath).parent.joinpath(DATLine.split('|')[0]))
        datResult[Audio] = DATLine.strip()
    return datResult


def DATResult_Save(datResult: list, datPath: str):
    """
    SaveDATResult
    """
    with open(datPath, mode = 'w', encoding = 'utf-8') as DAT:
        DATLines = '\n'.join(datResult)
        DAT.write(DATLines)

##############################################################################################################################