using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;
using System.Text;
using NRKernal;
using UnityEngine.UIElements;
using UnityEngine.EventSystems;


public class WorldSpawner : MonoBehaviour
{
    public static WorldSpawner instance;
    public GameObject wayPoint; //waypoint prefab
    public Transform World; //Container for World
    public Transform Coins; //Container for Coins
    public GameObject coinPrefab; //FH
    public WayPoint origin;
    public TMP_Text directionsText;
    private ParticleSystem pathParticles;
    //private List<Vector3> wayPointpositions = new List<Vector3>();
    //private float scalefactor = 1;
    public TMP_InputField test;
    public TMP_Text CoinCounter;
    private int currentCount;
    private int totalCount;

    private void Awake()
    {
        if (instance == null)
        {
            instance = this as WorldSpawner;
            DontDestroyOnLoad(gameObject); 
        }
        else if (instance != this)
        {
            Destroy(gameObject);
        }
        Input.compass.enabled = true;
        pathParticles = GetComponentInChildren<ParticleSystem>();
        if (pathParticles == null)
        {
            Debug.LogError("ParticleSystem component is missing on WorldSpawner. Please add it.");
        }
    }
    public void createWorld(List<WayPoint> points)
    {
        StringBuilder directionsBuilder = new StringBuilder();

        Vector3 originUnityPosition = LatLonToUnity(points[0].Latitude, points[0].Longitude, origin.Latitude, origin.Longitude);

        float heading = Input.compass.magneticHeading;
        Quaternion rotation = Quaternion.Euler(0, -heading, 0);
        Debug.LogWarning("Rotation: " + rotation.ToString());
        Debug.LogWarning("Heading: " + heading);
        World.transform.position = originUnityPosition;

        foreach (WayPoint point in points)
        {
            createWayPoint(point);
        }
        directionsBuilder.AppendLine($"Heading: {heading}, Rotation: {rotation}");
        directionsText.text = directionsBuilder.ToString();
        World.transform.position = new Vector3(0, 0, 0);
        World.Rotate(0, -heading, 0);
        List<Vector3> positions = new List<Vector3>();
        foreach (Transform item in World)
        {
            positions.Add(item.transform.position);
        }
        DrawLine(positions);
    }

    public void CollectCoint()
    {
        currentCount++;
        CoinCounter.text = currentCount+ "/" + totalCount;
    }
    /*private void DrawLine(List<Vector3> wayPointpositions)
    {
        renderer.positionCount = wayPointpositions.Count;
        renderer.SetPositions(wayPointpositions.ToArray());
       
        //Moved Coins here 
        // Calculate number of coins to place between waypoints
        int numberOfCoins = 5; // For example, 5 coins between each waypoint
        float step = 1.0f / (numberOfCoins + 1);

        for (int i = 0; i < wayPointpositions.Count-1; i++)
        {
            for (int j = 1; j <= numberOfCoins; j++)
            {
                Vector3 coinPosition = Vector3.Lerp(wayPointpositions[i], wayPointpositions[i+1], step * j);
                GameObject coin = Instantiate(coinPrefab, Coins);
                coin.transform.position = coinPosition + Vector3.up * 0.5f; // Adjust Y position to place the coin above the ground
                coin.transform.localScale *= 100.0f; // Adjust the scale as needed
                totalCount++;
            }  
        }
        CoinCounter.text = 0 + "/" + totalCount;

    }
    */
    private void DrawLine(List<Vector3> wayPointPositions)
    {
        if (pathParticles == null)
        {
            Debug.LogError("ParticleSystem is null. Make sure it is attached to WorldSpawner.");
            return;
        }

        
        ParticleSystem.TrailModule trailModule = pathParticles.trails;

        

        trailModule.enabled = true; 
        trailModule.widthOverTrail = new ParticleSystem.MinMaxCurve(0.1f, 0.5f);  
        trailModule.colorOverTrail = new ParticleSystem.MinMaxGradient(Color.yellow, Color.red);  

       

        ParticleSystem.EmitParams emitParams = new ParticleSystem.EmitParams();
        pathParticles.Clear();

        
        int particlesPerWaypoint = 10;  // Number of particles emitted per waypoint
        for (int i = 0; i < wayPointPositions.Count - 1; i++)
        {
            Vector3 startPos = wayPointPositions[i];
            Vector3 endPos = wayPointPositions[i + 1];

            
            for (int j = 0; j < particlesPerWaypoint; j++)
            {
                float t = j / (float)(particlesPerWaypoint - 1);  
                Vector3 position = Vector3.Lerp(startPos, endPos, t);

                emitParams.position = position;
                emitParams.startSize = 0.5f;  
                emitParams.startColor = Color.yellow;  

                
                pathParticles.Emit(emitParams, 1);
            }
        }


        int numberOfCoins = 5;
        float step = 1.0f / (numberOfCoins + 1);

        for (int i = 0; i < wayPointPositions.Count - 1; i++)
        {
            for (int j = 1; j <= numberOfCoins; j++)
            {
                Vector3 coinPosition = Vector3.Lerp(wayPointPositions[i], wayPointPositions[i + 1], step * j);
                GameObject coin = Instantiate(coinPrefab, Coins);
                coin.transform.position = coinPosition - Vector3.up * 1.25f; // Adjust Y position
                coin.transform.localScale *= 50.0f; // Adjust scale
                totalCount++;
            }
        }
        CoinCounter.text = $"0 / {totalCount}";
    }


    private void createWayPoint(WayPoint point)
    {
        Vector3 spawn = LatLonToUnity(point.Latitude, point.Longitude, origin.Latitude, origin.Longitude);
        GameObject waypoint = Instantiate(wayPoint, World);
        spawn.y -= 0.5f;
        waypoint.transform.position = spawn;
        waypoint.name = point.Instruction;
        //LH: Sets the text of the waypoint to the corresponding instruction
        waypoint.GetComponentInChildren<TMP_Text>().text = point.Instruction;
        //wayPointpositions.Add(spawn);
    }

    Vector3 LatLonToUnity(float latitude, float longitude, float originLat, float originLon)
    {
        // Earth's approximate radius in meters
        const float earthRadius = 6378137f;


        // Calculate latitude and longitude differences in radians
        float latDiff = (latitude - originLat) * Mathf.Deg2Rad;
        float lonDiff = (longitude - originLon) * Mathf.Deg2Rad;

        // Convert latitude difference to meters
        float latMeters = latDiff * earthRadius;

        // Convert longitude difference to meters, scaled by latitude
        float lonMeters = lonDiff * earthRadius * Mathf.Cos(originLat * Mathf.Deg2Rad);

        // Return as Unity coordinates (X = longitude, Z = latitude)
        return new Vector3(lonMeters, 0, latMeters);
    }
}
