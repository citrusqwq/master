using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class AutocompleteOptions : MonoBehaviour
{
    public float latitude;
    public float longitude;
    public string label;
    private LocationInputHandler handler;
    
    public void Instatiate(float latitude, float longitude, LocationInputHandler handler, string label)
    {
        this.latitude = latitude;
        this.longitude = longitude;
        this.handler = handler;
        this.label = label;
        GetComponentInChildren<TMP_Text>().text = label;
    }

    public void OnButtonClick()
    {
        handler.OptionInput(this);
        //LH hide suggestion Panel + show selection in inputField
        handler.destinationInputField.text = label;
        handler.dropDownContainer.gameObject.SetActive(false);

        Debug.Log(latitude);
        Debug.Log(longitude);
    }
}
