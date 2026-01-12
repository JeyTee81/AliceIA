/*
 * Client Unity C# pour communiquer avec l'IA personnelle.
 * Placez ce script dans votre projet Unity.
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
using Newtonsoft.Json;

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

public class IAPersonalClient : MonoBehaviour
{
    [Header("Configuration")]
    [SerializeField] private string apiUrl = "http://localhost:5000";
    [SerializeField] private float updateInterval = 0.5f; // Mise à jour de l'état toutes les 0.5s
    
    [Header("Events")]
    public UnityEngine.Events.UnityEvent<EmotionState> OnEmotionChanged;
    public UnityEngine.Events.UnityEvent<AvatarState> OnAvatarStateChanged;
    public UnityEngine.Events.UnityEvent<string> OnResponseReceived;
    
    private EmotionState currentEmotion;
    private AvatarState currentAvatarState;
    private Coroutine updateCoroutine;
    
    void Start()
    {
        // Vérifier la connexion
        StartCoroutine(CheckHealth());
        
        // Démarrer la mise à jour périodique
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
    
    /// <summary>
    /// Vérifie que le serveur API est accessible.
    /// </summary>
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
    /// Envoie un message à l'IA et récupère la réponse.
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
                    TalkResponse response = JsonConvert.DeserializeObject<TalkResponse>(request.downloadHandler.text);
                    
                    if (response.success)
                    {
                        currentEmotion = response.emotion;
                        OnEmotionChanged?.Invoke(response.emotion);
                        OnResponseReceived?.Invoke(response.response);
                        onResponse?.Invoke(response.response);
                    }
                    else
                    {
                        Debug.LogError($"Erreur IA: {request.downloadHandler.text}");
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
                    var response = JsonConvert.DeserializeObject<Dictionary<string, object>>(request.downloadHandler.text);
                    if (response.ContainsKey("emotion"))
                    {
                        EmotionState emotion = JsonConvert.DeserializeObject<EmotionState>(
                            response["emotion"].ToString()
                        );
                        currentEmotion = emotion;
                        OnEmotionChanged?.Invoke(emotion);
                        onEmotion?.Invoke(emotion);
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
    /// Récupère l'état de l'avatar (pour animations Unity).
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
                        AvatarStateResponse response = JsonConvert.DeserializeObject<AvatarStateResponse>(
                            request.downloadHandler.text
                        );
                        
                        if (response.success)
                        {
                            currentAvatarState = response.avatar;
                            currentEmotion = response.emotion;
                            
                            OnAvatarStateChanged?.Invoke(response.avatar);
                            OnEmotionChanged?.Invoke(response.emotion);
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
    
    /// <summary>
    /// Enseigne quelque chose à l'IA.
    /// </summary>
    public void Teach(string content, float importance = 0.7f, System.Action<string> onResponse = null)
    {
        StartCoroutine(TeachCoroutine(content, importance, onResponse));
    }
    
    IEnumerator TeachCoroutine(string content, float importance, System.Action<string> onResponse)
    {
        var requestData = new { content = content, importance = importance };
        string jsonData = JsonConvert.SerializeObject(requestData);
        
        using (UnityWebRequest request = new UnityWebRequest($"{apiUrl}/api/teach", "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                var response = JsonConvert.DeserializeObject<Dictionary<string, object>>(request.downloadHandler.text);
                if (response.ContainsKey("response"))
                {
                    onResponse?.Invoke(response["response"].ToString());
                }
            }
        }
    }
    
    // Getters pour l'état actuel
    public EmotionState GetCurrentEmotion() => currentEmotion;
    public AvatarState GetCurrentAvatarState() => currentAvatarState;
}
