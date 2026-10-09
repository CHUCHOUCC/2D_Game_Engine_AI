# 2D Engine · AI Service

Separate service that creates game objects for the 2D engine and **learns from every run**
played on a level, so the obstacles it places get harder (or easier) to keep the level fun.
Only the backend calls it; the frontend never talks to it.

```
Frontend -> Backend -> Database (stores each level's learned model)
               |
               +-- service token (JWT, 60 s) --> AI Service -> optional external AI API
```
