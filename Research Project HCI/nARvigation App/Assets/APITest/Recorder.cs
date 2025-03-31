using NRKernal.Record;
using UnityEngine;
using UnityEngine.UI;

public class Recorder : MonoBehaviour
{
    private NRVideoCapture videoCapture;
 

    void Start()
    {
        NRVideoCapture.CreateAsync(true, OnVideoCaptureCreated);
        
    }

    private void OnVideoCaptureCreated(NRVideoCapture capture)
    {
        if (capture == null)
        {
            Debug.LogError("Failed to create NRVideoCapture instance.");
            return;
        }
        videoCapture = capture;
    }

    public void StartRecording()
    {

        if (videoCapture == null)
        {
            Debug.LogError("NRVideoCapture is not initialized.");
            return;
        }

        //Debug.Log($"Recording with resolution {cameraResolutionWidth}x{cameraResolutionHeight}, format {pixelFormat}");
        Debug.Log($"File path: {System.IO.Path.Combine(Application.persistentDataPath, "RecordedVideo.mp4")}");

        var cameraParameters = new NRKernal.Record.CameraParameters
        {
            hologramOpacity = 0.0f, // Adjust as necessary
            frameRate = 30,
            cameraResolutionWidth = 1280,
            cameraResolutionHeight = 720,
            pixelFormat = NRKernal.Record.CapturePixelFormat.BGRA32,
        };

        string filePath = System.IO.Path.Combine(Application.persistentDataPath, "RecordedVideo.mp4");
        videoCapture.StartRecordingAsync(filePath, OnStartedRecordingVideo);

    }

    private void OnStartedRecordingVideo(NRVideoCapture.VideoCaptureResult result)
    {
        if (result.success)
        {
            Debug.Log("Recording started.");
        }
        else
        {
            Debug.LogError("Failed to start recording.");
        }
    }

    public void StopRecording()
    {
        if (videoCapture != null)
        {
            videoCapture.StopRecordingAsync(OnStoppedRecordingVideo);
        }
    }

    private void OnStoppedRecordingVideo(NRVideoCapture.VideoCaptureResult result)
    {
        if (result.success)
        {
            Debug.Log("Recording stopped. Video saved.");
        }
        else
        {
            Debug.LogError("Failed to stop recording.");
        }

        videoCapture.Dispose();
        videoCapture = null;
    }
}

