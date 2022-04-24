#!/bin/sh
cp earth.png bust.png
cp fire.png  stage.png
cp water.png void.png
cp wind.png  match.png
if [[ -f earth.png.mcmeta ]]; then cp earth.png.mcmeta bust.png.mcmeta ; else rm -f bust.png.mcmeta ; fi
if [[ -f fire.png.mcmeta  ]]; then cp fire.png.mcmeta  stage.png.mcmeta; else rm -f stage.png.mcmeta; fi
if [[ -f water.png.mcmeta ]]; then cp water.png.mcmeta void.png.mcmeta ; else rm -f void.png.mcmeta ; fi
if [[ -f wind.png.mcmeta  ]]; then cp wind.png.mcmeta  match.png.mcmeta; else rm -f match.png.mcmeta; fi
