/*
 * Client Unity C# simplifié (sans dépendances externes).
 * Utilise uniquement JsonUtility natif de Unity.
 * 
 * Utilisation:
 * 1. Créez un GameObject vide
 * 2. Ajoutez ce script comme composant
 * 3. Configurez l'URL du serveur (par défaut: http://localhost:5000)
 */

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.Events;

[System.Serializable]
public class EmotionState
{
    public float valence;
    public float arousal;
    public float dominance;
    public float confidence;
    public float curiosity;
    public float attachment;
    public float intensity;
    public string label;
}

[System.Serializable]
public class AvatarState
{
    public string expression;
    public string animation;
    public float intensity;
    public float eye_brightness;
    public string mouth_shape;
    public float head_tilt;
}

[System.Serializable]
public class TalkRequest
{
    public string message;
}

[System.Serializable]
public class TalkResponse
{
    public string response;
    public EmotionState emotion;
    public bool success;
}

[System.Serializable]
public class AvatarStateResponse
{
    public AvatarState avatar;
    public EmotionState emotion;
    public bool success;
}

[System.Serializable]
public class APIResponse<T>
{
    public T data;
    public bool success;
    public string error;
}

public class IAPersonalClientSimple : MonoBehaviour
{
    [Header("Configuration")]
    [SerializeField] private string apiUrl = "http://localhost:5000";
    [SerializeField] private float updateInterval = 0.5f;
    
    [Header("Events")]
    public UnityEvent<EmotionState> OnEmotionChanged;
    public UnityEvent<AvatarState> OnAvatarStateChanged;
    public UnityEvent<string> OnResponseReceived;
    
    private EmotionState currentEmotion;
    private AvatarState currentAvatarState;
    private Coroutine updateCoroutine;
    
    void Start()
    {
        StartCoroutine(CheckHealth());
        
        if (updateInterval > 0)
        {
            updateCoroutine = StartCoroutine(UpdateAvatarState());
        }
    }
    
    void OnDestroy()
    {
        if (updateCoroutine != null)
        {
            StopCoroutine(updateCoroutine);
        }
    }
    
    IEnumerator CheckHealth()
    {
        using (UnityWebRequest request = UnityWebRequest.Get($"{apiUrl}/api/health"))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("✅ Connexion à l'IA établie");
            }
            else
            {
                Debug.LogError($"❌ Impossible de se connecter à l'IA: {request.error}");
            }
        }
    }
    
    /// <summary>
    /// Envoie un message à l'IA.
    /// </summary>
    public void SendMessage(string message, System.Action<string> onResponse = null)
    {
        StartCoroutine(SendMessageCoroutine(message, onResponse));
    }
    
    IEnumerator SendMessageCoroutine(string message, System.Action<string> onResponse)
    {
        TalkRequest requestData = new TalkRequest { message = message };
        string jsonData = JsonUtility.ToJson(requestData);
        
        using (UnityWebRequest request = new UnityWebRequest($"{apiUrl}/api/talk", "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    TalkResponse response = JsonUtility.FromJson<TalkResponse>(request.downloadHandler.text);
                    
                    if (response.success)
                    {
                        currentEmotion = response.emotion;
                        OnEmotionChanged?.Invoke(response.emotion);
                        OnResponseReceived?.Invoke(response.response);
                        onResponse?.Invoke(response.response);
                    }
                }
                catch (Exception e)
                {
                    Debug.LogError($"Erreur parsing réponse: {e}");
                }
            }
            else
            {
                Debug.LogError($"Erreur requête: {request.error}");
            }
        }
    }
    
    /// <summary>
    /// Récupère l'état émotionnel actuel.
    /// </summary>
    public void GetEmotion(System.Action<EmotionState> onEmotion = null)
    {
        StartCoroutine(GetEmotionCoroutine(onEmotion));
    }
    
    IEnumerator GetEmotionCoroutine(System.Action<EmotionState> onEmotion)
    {
        using (UnityWebRequest request = UnityWebRequest.Get($"{apiUrl}/api/emotion"))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    // JsonUtility nécessite un wrapper pour les réponses avec objets imbriqués
                    string json = request.downloadHandler.text;
                    json = json.Replace("\"emotion\":", "\"data\":");
                    var wrapper = JsonUtility.FromJson<APIResponse<EmotionState>>(json);
                    
                    if (wrapper.success && wrapper.data != null)
                    {
                        currentEmotion = wrapper.data;
                        OnEmotionChanged?.Invoke(wrapper.data);
                        onEmotion?.Invoke(wrapper.data);
                    }
                }
                catch (Exception e)
                {
                    Debug.LogError($"Erreur parsing émotion: {e}");
                }
            }
        }
    }
    
    /// <summary>
    /// Récupère l'état de l'avatar (mise à jour automatique).
    /// </summary>
    IEnumerator UpdateAvatarState()
    {
        while (true)
        {
            yield return new WaitForSeconds(updateInterval);
            
            using (UnityWebRequest request = UnityWebRequest.Get($"{apiUrl}/api/avatar/state"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        string json = request.downloadHandler.text;
                        // Adapter le JSON pour JsonUtility
                        json = json.Replace("\"avatar\":", "\"data\":");
                        var wrapper = JsonUtility.FromJson<APIResponse<AvatarStateResponse>>(json);
                        
                        if (wrapper.success && wrapper.data != null)
                        {
                            currentAvatarState = wrapper.data.avatar;
                            currentEmotion = wrapper.data.emotion;
                            
                            OnAvatarStateChanged?.Invoke(wrapper.data.avatar);
                            OnEmotionChanged?.Invoke(wrapper.data.emotion);
                        }
                    }
                    catch (Exception e)
                    {
                        Debug.LogError($"Erreur parsing avatar state: {e}");
                    }
                }
            }
        }
    }
    
    // Getters
    public EmotionState GetCurrentEmotion() => currentEmotion;
    public AvatarState GetCurrentAvatarState() => currentAvatarState;
}
