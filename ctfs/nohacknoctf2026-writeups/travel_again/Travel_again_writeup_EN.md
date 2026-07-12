# NoHackNoCTF 2026 — `Travel again` Writeup

- **Author:** Efe Şahinbaş
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** OSINT  
**Difficulty:** 500  
**Goal:** Identify the location of the object visible in the photo  
**Flag format:** `NHNC{latitude,longitude}`  
**Coordinate rule:** Truncate both latitude and longitude to 4 decimal places. Do not round.

---

## Challenge Description

> I snapped a photo while passing through a location during my trip. Since the car never stopped, the photo is all I have. I've forgotten where it was—can you identify the location?
>
> Flag format: `NHNC{latitude,longitude}`  
> Truncate both the latitude and longitude to 4 decimal places.  
> Example: `NHNC{25.0339,121.5645}`
>
> Hint: `Not the shooting spot — the object itself.`

---

## Summary

This challenge provides a snowy roadside photo taken from a moving car. At first glance, the image looks sparse: a wide snow-covered field, distant mountains, a small arched structure, and a small sign or platform in the foreground.

The critical part of the challenge is the hint:

```text
Not the shooting spot — the object itself.
```

This means the target is not the exact position of the camera or the road where the photo was taken. The coordinates must point to the object visible in the frame.

By treating the object as the main search target and validating the surrounding environment, the location was identified as a farm object/structure in Shikaoi, Hokkaido, Japan. The matching coordinates are:

```text
43.1849,143.0325
```

Final flag:

```text
NHNC{43.1849,143.0325}
```

---

## 1. Reading the Image

The photo contains a few useful visual clues:

![Challenge Image](./images/travel_again.jpg)

Important elements:

- A large snow-covered open field
- Low mountains in the background
- A rural agricultural landscape
- A small arched-roof building or barn-like structure
- A small sign or platform in front of the object
- No dense urban features
- No clearly visible road signs or storefront names

The image does not provide a direct readable location name, so the solution depends on visual geolocation rather than text extraction.

The most valuable feature is the isolated object in the field. Snow, mountains, and open farmland are useful for region narrowing, but the object itself is the stronger anchor.

---

## 2. Understanding the Hint

The hint says:

```text
Not the shooting spot — the object itself.
```

This changes the search strategy.

A common mistake would be to search for the road, the exact camera position, or the route taken by the vehicle. However, the challenge asks for the coordinates of the visible object.

So the correct approach is:

```text
1. Identify the object visible in the photo.
2. Match it with satellite/street-level imagery or indexed web information.
3. Confirm that the surrounding terrain fits the photo.
4. Submit the coordinates of the object, not the photographer.
```

---

## 3. Region Narrowing

The scene strongly suggests northern Japan, especially Hokkaido:

- Extensive snow coverage
- Large agricultural fields
- Low mountain ridges
- Rural dairy-farm-style landscape

The final location falls within Shikaoi, a town in the Tokachi region of Hokkaido. This fit is consistent with the image: Shikaoi is located on the Tokachi Plain, with open farmland and mountains connected to the Daisetsuzan area in the wider landscape.

The area is also associated with agricultural and dairy activity, which matches the barn/farm-like object visible in the challenge image.

---

## 4. Object-Based Matching

Since the challenge explicitly tells us to focus on the object, the search should not start with generic terms like:

```text
snow field Hokkaido mountains
```

Those terms return too many visually similar results.

A better approach is to search around object-specific and region-specific terms:

```text
Hokkaido snow field farm arched barn
Tokachi snow field dairy farm
Shikaoi Hokkaido dairy farm snow
鹿追町 牧場 雪
鹿追町 酪農 牧場
北鹿追 牧場
```

The object and surroundings eventually point to the Shikaoi / Kita-Shikaoi area. The relevant farm identity is Nakano Farm / 株式会社中野牧場.

The farm’s listed address is:

```text
北海道河東郡鹿追町北鹿追北10線3番地55
```

This aligns with the coordinate area used for the final flag.

---

## 5. Verification

The match was verified through several consistency checks:

### Visual consistency

The challenge image shows:

- A snow-covered agricultural field
- A rural farm object
- Distant mountain terrain
- A sparse Tokachi-style landscape

This matches the expected environment around Shikaoi, Hokkaido.

### Geographic consistency

Shikaoi is located in the Tokachi region of Hokkaido. The region contains broad agricultural land, open plains, dairy farms, and mountain backdrops.

### Object-location consistency

The identified object is associated with Nakano Farm in Kita-Shikaoi. The address information points to:

```text
北海道河東郡鹿追町北鹿追北10線3番地55
```

The coordinates corresponding to the matched object/location are:

```text
43.1849,143.0325
```

---

## 6. Truncating the Coordinates

The challenge specifically requires truncation to 4 decimal places, not rounding.

The final coordinate pair is already in the required 4-decimal format:

```text
43.1849,143.0325
```

So the flag should be built as:

```text
NHNC{latitude,longitude}
```

Result:

```text
NHNC{43.1849,143.0325}
```

---

## 7. Final Flag

```text
NHNC{43.1849,143.0325}
```

---

## Key Takeaways

This challenge is a good reminder that OSINT geolocation is not always about finding the photographer’s exact position.

The hint was the key:

```text
Not the shooting spot — the object itself.
```

The correct workflow was:

```text
1. Ignore the camera position.
2. Use the visible object as the search anchor.
3. Narrow the region through environmental clues.
4. Validate the object against the surrounding terrain.
5. Submit the object’s coordinates, truncated to 4 decimals.
```

---

## References Used During Verification

- Nakano Farm official company information
- Shikaoi Town company/job listing for 株式会社中野牧場
- Shikaoi tourism and geopark pages for regional context
