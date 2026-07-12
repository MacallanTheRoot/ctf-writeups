# NoHackNoCTF 2026 — `Final Boarding` Writeup

- **Author:** Efe Şahinbaş
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Misc / OSINT  
**Goal:** Identify the date and the IATA flight number from the aircraft shown in the photo  
**Flag format:** `NHNC{YYYYMMDD_FLIGHT}`

---

## Challenge Description

> On the last day of the trip, I stood in front of the boarding gate, ready to board my flight home.
>
> That day in Japan marked the end of Golden Week, and the airport was packed with travelers preparing to return home.
>
> Before boarding, I took a photo of the aircraft in front of me; it was the flight I was about to take.
>
> Based on the aircraft information in the photo and the clues in the challenge, find:
>
> - The date the photo was taken
> - The IATA flight number of the flight I boarded
>
> Flag format: `NHNC{YYYYMMDD_FLIGHT}`
>
> Please use the IATA flight number, such as `BR198`, not the ICAO callsign.

---

## Summary

This challenge required identifying a specific flight from a single airport photo. The key was to extract aircraft information from the image, then combine it with the date clue given in the challenge text.

The aircraft in the photo was a Jetstar Japan Airbus A320 with the registration `JA06JJ`. The challenge also stated that the photo was taken at the end of Japan’s Golden Week, which narrowed the date range to early May 2026.

By correlating the aircraft registration, the airport context, and Jetstar Japan’s route information, the matching flight was identified as Jetstar Japan flight `GK55` from Osaka Kansai to Taipei Taoyuan.

Result:

```text
Date: 2026-05-05
IATA Flight Number: GK55
Flag: NHNC{20260505_GK55}
```

---

## 1. Extracting Clues from the Photo

The first step was to inspect the visible aircraft details.

![Final Boarding challenge image](./images/Final_boarding.png)

The useful clues were:

```text
Airline / Operator: Jetstar Japan
Aircraft Registration: JA06JJ
Aircraft Type: Airbus A320
Airport Context: Kansai International Airport-like apron and terminal environment
```

The Jetstar branding is visible on the fuselage and tail. More importantly, the registration `JA06JJ` can be read on the rear fuselage. This was the strongest OSINT pivot because an aircraft registration uniquely identifies a specific airframe.

---

## 2. Pivoting from the Aircraft Registration

The registration found in the image was:

```text
JA06JJ
```

This registration corresponds to a Jetstar Japan Airbus A320. Instead of searching randomly for Jetstar Japan flights, I used the registration as the primary search pivot.

The investigation flow was:

```text
1. Read the aircraft registration from the image: JA06JJ
2. Check aircraft tracking / flight history records for JA06JJ
3. Filter the results around the end of Golden Week
4. Compare matching routes and IATA flight numbers
```

This reduced the search space significantly.

---

## 3. Date Clue: The End of Golden Week

The most important date clue in the challenge text was:

```text
That day in Japan marked the end of Golden Week.
```

Golden Week is one of Japan’s busiest travel periods, taking place from late April to early May. Since the challenge was asking for a specific date, this clue narrowed the target range to the closing days of Golden Week in 2026.

The date used for the challenge solution was:

```text
2026-05-05
```

In the required flag format, this becomes:

```text
20260505
```

> Note: The date in this writeup is derived from the challenge text, the Golden Week clue, and the flight correlation. It is not based on EXIF metadata from the uploaded image.

---

## 4. Matching the Airport and Route

The apron layout, terminal/jet bridge environment, ground service vehicles, and Jetstar Japan operation context were consistent with Osaka Kansai International Airport.

The matching route was:

```text
Departure: Osaka Kansai International Airport (KIX)
Arrival: Taipei Taoyuan International Airport (TPE)
Airline: Jetstar Japan
Flight: GK55
```

The challenge specifically requested the IATA flight number, not the ICAO callsign. Therefore, the correct format is:

```text
GK55
```

not:

```text
JJP55
```

---

## 5. Why `GK55`?

The aircraft in the photo was Jetstar Japan’s `JA06JJ`, an Airbus A320. After checking the flight history and route information around the Golden Week clue, the matching service was Jetstar Japan’s Osaka Kansai to Taipei Taoyuan route.

The relevant correlation was:

```text
Registration: JA06JJ
Operator: Jetstar Japan
Aircraft: Airbus A320
Route: KIX → TPE
IATA Flight Number: GK55
```

Therefore, the flight number required for the flag was:

```text
GK55
```

---

## 6. Building the Flag

The required format was:

```text
NHNC{YYYYMMDD_FLIGHT}
```

The identified values were:

```text
YYYYMMDD = 20260505
FLIGHT   = GK55
```

Final flag:

```text
NHNC{20260505_GK55}
```

---

## Conclusion

The solution depended on combining visual aircraft identification with flight-history OSINT.

The main steps were:

```text
1. Read the aircraft registration from the image: JA06JJ
2. Map the registration to a Jetstar Japan Airbus A320
3. Use the Golden Week clue to narrow the date
4. Match the route and IATA flight number
```

Final flag:

```text
NHNC{20260505_GK55}
```
