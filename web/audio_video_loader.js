import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "Comfyui_NZ_ASR.AudioVideoLoader",
    async setup() {
        // 注册音频视频加载节点的上传功能
        const LoadAudioVideoNode = app.graph._nodes.filter(n => n.type === "LoadAudioVideo")[0]?.constructor;
        if (LoadAudioVideoNode) {
            const onNodeCreated = LoadAudioVideoNode.prototype.onNodeCreated;
            LoadAudioVideoNode.prototype.onNodeCreated = function() {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                // 添加上传按钮
                const uploadWidget = this.addWidget(
                    "button", 
                    "上传音频/视频", 
                    "上传", 
                    () => {
                        // 创建文件输入元素
                        const fileInput = document.createElement("input");
                        fileInput.type = "file";
                        fileInput.accept = ".wav,.mp3,.flac,.ogg,.mp4,.avi,.mov,.mkv,.webm";
                        fileInput.style.display = "none";
                        document.body.appendChild(fileInput);
                        
                        // 监听文件选择事件
                        fileInput.onchange = async () => {
                            if (!fileInput.files || !fileInput.files[0]) {
                                document.body.removeChild(fileInput);
                                return;
                            }
                            
                            const file = fileInput.files[0];
                            
                            try {
                                // 上传文件
                                const formData = new FormData();
                                formData.append("upload", file);
                                formData.append("overwrite", "true");
                                
                                const resp = await api.fetchApi("/upload/image", {
                                    method: "POST",
                                    body: formData,
                                });
                                
                                if (resp.status === 200) {
                                    const data = await resp.json();
                                    // 设置文件路径到节点输入
                                    if (data.name) {
                                        const filePath = "upload:" + data.name;
                                        this.widgets.find(w => w.name === "audio_video").value = filePath;
                                        // 触发节点更新
                                        this.onResize();
                                        app.graph.setDirtyCanvas(true);
                                    }
                                } else {
                                    alert("上传失败: " + resp.statusText);
                                }
                            } catch (error) {
                                alert("上传失败: " + error.message);
                            } finally {
                                document.body.removeChild(fileInput);
                            }
                        };
                        
                        // 触发文件选择对话框
                        fileInput.click();
                    }
                );
                
                // 添加文件路径输入框
                const pathWidget = this.widgets.find(w => w.name === "audio_video");
                if (pathWidget) {
                    pathWidget.options = {};
                }
                
                return r;
            };
        }
    },
});