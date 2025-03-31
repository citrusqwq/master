
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

public class WayPoint
{
    public float Latitude { get; set; }
    public float Longitude { get; set; }

    public string Instruction { get; set; } // Holds the instruction for the point
    public GameObject WaypointPrefab;

    public WayPoint(float latitude, float longitude, string instruction)
    {
        Latitude = latitude;
        Longitude = longitude;
        Instruction = instruction;

    }

    /*public static List<WayPoint> ExtractWaypointsWithInstructions(RouteResponse featureCollection)
    {
        var geometryPoints = new List<WayPoint>();

        foreach (var feature in featureCollection.features)
        {
            var geometryCoordinates = feature.geometry?.coordinates;
            var segments = feature.properties?.segments;

            if (geometryCoordinates != null && segments != null)
            {
                foreach (var segment in segments)
                {
                    foreach (var step in segment.steps)
                    {
                        // Link instructions to corresponding geometry points
                        foreach (var waypointIndex in step.way_points)
                        {
                            if (waypointIndex < geometryCoordinates.Count)
                            {
                                var coord = geometryCoordinates[waypointIndex];
                                geometryPoints.Add(new WayPoint(coord[1], coord[0], step.instruction));
                            }
                        }
                    }
                }
            }
        }

        return geometryPoints;
    }
    public static List<WayPoint> ExtractCentralWaypointsWithInstructions(RouteResponse routeResponse)
    {
        var centralWaypoints = new List<WayPoint>();

        if (routeResponse?.features == null) // Ensure featureCollection and Features are not null
            return centralWaypoints;

        foreach (var feature in routeResponse.features)
        {
            var geometryCoordinates = feature.geometry?.coordinates;
            var segments = feature.properties?.segments;

            if (geometryCoordinates == null || segments == null) // Skip if geometry or segments are null
                continue;

            foreach (var segment in segments)
            {
                if (segment?.steps == null) // Ensure Steps are not null
                    continue;

                foreach (var step in segment.steps)
                {
                    if (step?.way_points == null || step.way_points.Count == 0) // Skip steps with no waypoints
                        continue;

                    // Get the first waypoint index in the range
                    int centralWaypointIndex = step.way_points[0];

                    // Ensure the index is within bounds of the coordinates array
                    if (centralWaypointIndex < geometryCoordinates.Count)
                    {
                        var coord = geometryCoordinates[centralWaypointIndex];
                        centralWaypoints.Add(new WayPoint(coord[1], coord[0], step.instruction));
                    }
                }
            }
        }

        return centralWaypoints;
    }*/

    public static List<WayPoint> Extraction(RouteResponse response)
    {
        var wayPoints = new List<WayPoint>();
        var instruction = new List<InstructionWaymark>();
        foreach (var feature in response.features)
        {
            var geometryCoordinates = feature.geometry?.coordinates;
            var segments = feature.properties?.segments;
            foreach (var segment in segments)
            {
                foreach (var item in segment.steps)
                {
                    instruction.Add(new InstructionWaymark(item.instruction, item.way_points[0], item.way_points[1]));
                    Debug.Log(item.instruction);
                }
            }
            
            int instructionCounter = 0;

            for (var i = 0; i < geometryCoordinates.Count; i++)
            {
                if ((instruction[instructionCounter].end <= i))
                {
                    Debug.LogWarning(instructionCounter);
                    instructionCounter++;
                }
                if (instruction[instructionCounter].start == i) {
                    wayPoints.Add(new WayPoint(geometryCoordinates[i][1], geometryCoordinates[i][0], instruction[instructionCounter].instruction));
                }
                else
                {
                    wayPoints.Add(new WayPoint(geometryCoordinates[i][1], geometryCoordinates[i][0], ""));
                }
            }          

        }

        return wayPoints;
    }

    private class InstructionWaymark
    {
        public string instruction;
        public int start;
        public int end;

        public InstructionWaymark(string instruction, int start, int end )
        {
            this.instruction = instruction;
            this.start = start;
            this.end = end;
        }
    }
}
