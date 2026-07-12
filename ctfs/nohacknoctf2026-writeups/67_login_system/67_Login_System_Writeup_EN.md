# NoHackNoCTF 2026 — `67 Login System` Writeup

- **Author:** Efe Şahinbaş
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Web / Reverse Engineering  
**Target:** `http://chal2.teagod.tech:8003/`  
**Challenge description:**

```text
Who is Whois?
http://chal2.teagod.tech:8003/

This is not a part of challenge don't break it
```

---

## Summary

At first glance, this challenge looked like a normal login system. The landing page redirected to a sign-in page, and the login page contained a standard username/password form. However, the form itself was not the real target.

The important clue was visible directly in the HTML/UI:

```text
This is a demonstration login; any credentials will succeed.
```

That line made it clear that this was not a password guessing challenge. The frontend login flow was mostly decorative. The actual logic was hidden inside the backend application, where a token/secret-based control path eventually led to the flag.

The solution was based on inspecting the deployed ASP.NET application files and reading the logic inside the backend DLL.

Final flag:

```text
NHNC{gggggggggggggggggggggggggggggggggggggggggggggggggggg_sixseven!!!}
```

---

## 1. Initial Recon

After opening the service, the landing page did not expose any sensitive information. It only redirected to the login page.

The login page contained a basic form:

- username field
- password field
- `POST /login` request
- simple sign-in flow

At first, it looked like a typical authentication challenge where brute-force, SQL injection, or login bypass could be relevant. However, the page itself contained the key hint:

```text
This is a demonstration login; any credentials will succeed.
```

This changed the direction of the analysis. The goal was not to find valid credentials, but to understand what the backend did after a successful login.

---

## 2. The Role of the Frontend

The frontend accepted arbitrary credentials. This showed that it was not enforcing a meaningful authentication check.

The main conclusion was:

```text
The frontend is only part of the user flow.
The actual challenge logic is in the backend.
```

Because of this, repeatedly testing the login form in the browser was not useful. The better approach was to inspect the challenge files directly.

---

## 3. Inspecting the Challenge Files

The provided files looked like an ASP.NET deployment output. The most relevant files were:

```text
Login-page.dll
Login-page.deps.json
Login-page.runtimeconfig.json
wwwroot/index.html
wwwroot/login.html
```

The `wwwroot` directory contained the static frontend files. The real application logic was inside `Login-page.dll`.

The Docker configuration also confirmed that the service was started with:

```bash
dotnet Login-page.dll
```

This confirmed that the backend DLL was the main analysis target.

---

## 4. String Analysis on the DLL

The first step was to run a string search on the DLL. In .NET challenges, strings often reveal endpoint names, route definitions, token variables, and secret checks.

The interesting strings were:

```text
tokenStore
token
adminSecret
MapGet
MapPost
```

These names were enough to infer several things:

1. The application stores or tracks tokens.
2. There is a special value named `adminSecret`.
3. The application likely uses route-based ASP.NET minimal API handlers.
4. The flag path is probably tied to a token or secret validation flow, not to the username/password fields.

---

## 5. Understanding the Backend Flow

The `MapGet` and `MapPost` strings indicated that routes were defined inside the backend. This meant the static HTML files were only the visible part of the challenge, while the real checks happened in the application logic.

The backend behavior can be summarized as follows:

```text
1. The user logs in with any credentials.
2. The backend creates or stores a token/state value.
3. An admin/secret check is performed through that token flow.
4. If the correct internal value is reached, the flag is returned.
```

The challenge title, `Who is Whois?`, also fits this interpretation. The important question is not “what is the password?”, but “how does the backend decide who is admin or privileged?”

---

## 6. Why This Was Not a Classic Login Attack

The following approaches were not the intended path:

- username/password brute-force
- basic SQL injection
- changing only the HTML
- modifying the form action
- randomly guessing cookies or tokens

The challenge already stated that any credentials would succeed. Therefore, the correct approach was to analyze what happened after login and how the backend handled token/secret state.

---

## 7. Getting the Flag

After analyzing the backend logic and following the token/secret-based control flow, the final flag was verified as:

```text
NHNC{gggggggggggggggggggggggggggggggggggggggggggggggggggg_sixseven!!!}
```

---

## 8. Conclusion

Although this challenge looked like a simple login page from the outside, it was closer to a web + reverse engineering problem.

The solution path was:

```text
1. Inspect the landing page and login form.
2. Notice that the login form does not perform real credential validation.
3. Inspect the ASP.NET deployment files.
4. Analyze Login-page.dll.
5. Find tokenStore, token, adminSecret, MapGet, and MapPost strings.
6. Infer the backend token/secret flow.
7. Validate the correct value and retrieve the flag.
```

Final flag:

```text
NHNC{gggggggggggggggggggggggggggggggggggggggggggggggggggg_sixseven!!!}
```

---

## Note

In challenges like this, the frontend does not always represent the real problem. When a page explicitly says that any credentials will work, the login form is usually a distraction. The useful information is more likely to be in backend routes, token generation, or secret comparison logic.
