using UnityEngine;
using UnityEngine.Networking;
using TMPro;
using System.Collections;
using System.Text;
using System;
using System.Globalization;
using System.Collections.Generic;
//using Palmmedia.ReportGenerator.Core.Common;
//using OpenCover.Framework.Model;
using Newtonsoft.Json;


public class LocationInputHandler : MonoBehaviour
{
    public TMP_InputField destinationInputField;
    public TMP_Text displayText;
    public TMP_Text directionsText;
    public Transform dropDownContainer;
    private string apiKey = "5b3ce3597851110001cf6248a8e8c1d08a624e5db1360921f3ee5edb"; // Replace with your OpenRouteService API key
    public GameObject AutocompleteOptionPrefab;

    public void OnButtonClick()
    {
        //LH show suggestion Panel
        dropDownContainer.gameObject.SetActive(true);

        string destination = destinationInputField.text;
        StartCoroutine(AutocompleteInput(destination));
    }

    private IEnumerator FetchAndDisplayLocation(AutocompleteOptions destination)
    {
        displayText.text = "Getting current location...";
        
        if (!Input.location.isEnabledByUser)
        {
            displayText.text = "Location services are disabled. Please enable them in settings.";
            StartCoroutine(FetchRouteDirections(52.382286f, 9.717809f, destination.latitude, destination.longitude));
            yield break;
        }

        Input.location.Start();
        int maxWait = 20;
        while (Input.location.status == LocationServiceStatus.Initializing && maxWait > 0)
        {
            yield return new WaitForSeconds(1);
            maxWait--;
        }

        if (maxWait < 1 || Input.location.status == LocationServiceStatus.Failed)
        {
            displayText.text = "Unable to determine device location.";
            yield break;
        }

        float userLatitude = Input.location.lastData.latitude;
        float userLongitude = Input.location.lastData.longitude;
        WorldSpawner.instance.origin = new WayPoint(userLatitude, userLongitude, "Origin");

        displayText.text = "Fetching destination coordinates...";

        //StartCoroutine(FetchDestinationCoordinates(destination, userLatitude, userLongitude));
        StartCoroutine(FetchRouteDirections(userLatitude, userLongitude, destination.latitude, destination.longitude));
        Input.location.Stop();
    }

    public void test()
    {
        WorldSpawner.instance.origin = new WayPoint(52.382286f, 9.717809f, "Origin");
        StartCoroutine(AutocompleteInput("Welfengarten"));

    }

    private IEnumerator AutocompleteInput(string destination) 
    {
        string url = $"https://api.openrouteservice.org/geocode/autocomplete?api_key={apiKey}&text={UnityWebRequest.EscapeURL(destination)}&size=5";
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
            {
                displayText.text = "Failed to retrieve destination coordinates.";
                Debug.LogError(request.error);
            }
            else
            {
                var json = request.downloadHandler.text;
                var geocodeResponse = JsonUtility.FromJson<GeocodeAutocompleteResponse>(json);

                if (geocodeResponse.features.Length > 0)
                {
                    //CleanUp
                    foreach (Transform child in dropDownContainer)
                    {
                        Destroy(child.gameObject);
                    }
                    // Build a list of names from all features
                    StringBuilder namesBuilder = new StringBuilder("Locations Found:\n");
                    List<String> names = new List<String>();
                    List<AutocompleteOptions> options = new List<AutocompleteOptions>();

                    for (int i = 0; i < geocodeResponse.features.Length; i++)
                    {
                        if (!names.Contains(geocodeResponse.features[i].properties.label))
                        {
                            namesBuilder.AppendLine(geocodeResponse.features[i].properties.label);
                            names.Add(geocodeResponse.features[i].properties.label);
                            //Instantiate of DropdownMenu
                            GameObject button = Instantiate(AutocompleteOptionPrefab, dropDownContainer);
                            button.GetComponent<AutocompleteOptions>().Instatiate(geocodeResponse.features[i].geometry.coordinates[1], geocodeResponse.features[0].geometry.coordinates[0], this, geocodeResponse.features[i].properties.label);
                            //options.Add(new AutocompleteOptions(geocodeResponse.features[i].geometry.coordinates[1], geocodeResponse.features[0].geometry.coordinates[0], this, geocodeResponse.features[i].properties.label));
                        }
                    }

                    // Display the list of names
                    displayText.text = namesBuilder.ToString();
                    //buildDropdownMenu(options);
                }
                else
                {
                    displayText.text = "No locations found for the destination.";
                }

            }
        }
    }

    /*private void buildDropdownMenu(List<AutocompleteOptions> options)
    {
        foreach (AutocompleteOptions option in options)
        {
            GameObject button = Instantiate(AutocompleteOptionPrefab, dropDownContainer);
        }
    }*/

    /*private IEnumerator FetchDestinationCoordinates(string destination, float userLatitude, float userLongitude)
{
   string url = $"https://api.openrouteservice.org/geocode/search?api_key={apiKey}&text={UnityWebRequest.EscapeURL(destination)}";

   using (UnityWebRequest request = UnityWebRequest.Get(url))
   {
       yield return request.SendWebRequest();

       if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
       {
           displayText.text = "Failed to retrieve destination coordinates.";
           Debug.LogError(request.error);
       }
       else
       {
           var json = request.downloadHandler.text;
           Debug.Log(request.downloadHandler.text);
           var geocodeResponse = JsonUtility.FromJson<GeocodeResponse>(json);

           if (geocodeResponse.features.Length > 0)
           {
               float destinationLatitude = geocodeResponse.features[0].geometry.coordinates[1];
               float destinationLongitude = geocodeResponse.features[0].geometry.coordinates[0];

               displayText.text = $"Current Location: Lon {userLongitude}, Lat {userLatitude} \n" +
                                  $"Destination Coordinates: Lon {destinationLongitude}, Lat {destinationLatitude} ";

               // Fetch route directions
               StartCoroutine(FetchRouteDirections(userLatitude, userLongitude, destinationLatitude, destinationLongitude));
           }
           else
           {
               displayText.text = "No location found for the destination.";
           }

       }
   }
}*/

    public void OptionInput(AutocompleteOptions destination)
    {
        StartCoroutine(FetchAndDisplayLocation(destination));
    }

    private IEnumerator FetchRouteDirections(float startLat, float startLon, float endLat, float endLon)
{
    // Force decimal points for latitude and longitude formatting
    string formattedStartLat = startLat.ToString(CultureInfo.InvariantCulture);
    string formattedStartLon = startLon.ToString(CultureInfo.InvariantCulture);
    string formattedEndLat = endLat.ToString(CultureInfo.InvariantCulture);
    string formattedEndLon = endLon.ToString(CultureInfo.InvariantCulture);

    string url = $"https://api.openrouteservice.org/v2/directions/foot-walking?api_key={apiKey}&start={formattedStartLon},{formattedStartLat}&end={formattedEndLon},{formattedEndLat}";

    directionsText.text = "Calculating route...";

    using (UnityWebRequest request = UnityWebRequest.Get(url))
    {
        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
        {
            directionsText.text = "Failed to retrieve directions.";
            Debug.LogError(request.error);
        }
        else
        {
            // Parse and display the step-by-step directions
            var json = request.downloadHandler.text;
            Debug.Log(json);
            var routeResponse = JsonConvert.DeserializeObject<RouteResponse>(json);

                StringBuilder directionsBuilder = new StringBuilder();
               

            foreach (var segment in routeResponse.features[0].properties.segments)
            {
                foreach (var step in segment.steps)
                {
                    directionsBuilder.AppendLine($"{step.instruction} for {step.distance} meters.");
                }
            }




                 //Extract geometry points with instructions
                List<WayPoint> geometryPoints = WayPoint.Extraction(routeResponse);
                if (geometryPoints != null && geometryPoints.Count > 0)
            {
                // Create a string builder to concatenate the waypoint details
                System.Text.StringBuilder sb = new System.Text.StringBuilder();

                foreach (var waypoint in geometryPoints)
                {
                    sb.AppendLine($"Latitude: {waypoint.Latitude}");
                    sb.AppendLine($"Longitude: {waypoint.Longitude}");
                    sb.AppendLine($"Instruction: {waypoint.Instruction}");
                    sb.AppendLine("------------------------");
                }

                // Set the concatenated string to the text field
                displayText.text = sb.ToString();
            }
            else
            {
                // If no waypoints are found, display a default message
                displayText.text = "No waypoints found.";
            }


                foreach (var point in geometryPoints)
                {
                    Debug.Log($"Latitude: {point.Latitude}, Longitude: {point.Longitude}, Instruction: {point.Instruction}");
                }

                WorldSpawner.instance.createWorld(geometryPoints);
            }
    }
}
}

// Define classes to parse JSON response
[System.Serializable]
public class GeocodeResponse
{
    public Feature[] features;
}

/*[System.Serializable]
public class Feature
{
    public Geometry geometry;
}*/

[System.Serializable]
public class Geometry
{
    public float[] coordinates;
}


[System.Serializable]
public class RouteResponse
{
    public FeatureRoute[] features;
}

[System.Serializable]
public class FeatureRoute
{
    public string type;
    public float[] bbox;
    public Properties properties;
    public geometry geometry;
}


[System.Serializable]
public class geometry
{
    public string type { get; set; }
    public List<float[]> coordinates; 
    
}


[System.Serializable]
public class Properties
{
    public Segment[] segments;
    public List<int> way_points { get; set; }
    public Summary summary { get; set; }
}

[System.Serializable]
public class Segment
{
    public double distance { get; set; }
    public double duration { get; set; }
    public Step[] steps;
}

[System.Serializable]
public class Step
{
    public float distance;
    public double duration { get; set; }
    public int type { get; set; }
    public string instruction;

    public string name { get; set; }
    public List<int> way_points { get; set; }
}

public class Summary
{
    public double distance { get; set; }
    public double duration { get; set; }
}

/////
[System.Serializable]
public class GeocodeAutocompleteResponse
{
    public Geocoding geocoding;
    public string type;
    public Feature[] features;
    public float[] bbox;
}

[System.Serializable]
public class Geocoding
{
    public string version;
    public string attribution;
    public Query query;
    public string[] warnings;
    public Engine engine;
    public long timestamp;
}

[System.Serializable]
public class Query
{
    public string text;
    public string parser;
    public ParsedText parsed_text;
    public int size;
    public string[] layers;
    public bool @private;
    public Lang lang;
    public int querySize;
}

[System.Serializable]
public class ParsedText
{
    public string subject;
    public string locality;
}

[System.Serializable]
public class Lang
{
    public string name;
    public string iso6391;
    public string iso6393;
    public string via;
    public bool defaulted;
}

[System.Serializable]
public class Engine
{
    public string name;
    public string author;
    public string version;
}

[System.Serializable]
public class Feature
{
    public string type;
    public Geometry geometry;
    public FeatureProperties properties;
    public float[] bbox;
}

[System.Serializable]
public class FeatureProperties
{
    public string id;
    public string gid;
    public string layer;
    public string source;
    public string source_id;
    public string name;
    public string accuracy;
    public string country;
    public string country_gid;
    public string country_a;
    public string region;
    public string region_gid;
    public string region_a;
    public string county;
    public string county_gid;
    public string locality;
    public string locality_gid;
    public string continent;
    public string continent_gid;
    public string label;
    public Addendum addendum;
}

[System.Serializable]
public class Addendum
{
    public Concordances concordances;
    public Geonames geonames;
}

[System.Serializable]
public class Concordances
{
    public string dbp_id;
    public string fb_id;
    public string fct_id;
    public int gn_id;
    public int gp_id;
    public string loc_id;
    public string nyt_id;
    public int qs_pg_id;
}

[System.Serializable]
public class Geonames
{
    public string feature_code;
}

