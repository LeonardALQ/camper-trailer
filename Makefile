# Camper trailer design site: data -> model -> trailer layout -> checks -> drawings -> site.
# Every stage runs in the project Docker image, so the build only needs Docker and make on the host.
#   make            all stages from scratch (checks never stop the build; their result is reported)
#   make strict     the same, but fail if any design check fails
#   make serve      serve site/dist on 127.0.0.1:8791
#   make shots      headless screenshots and scroll checks (Playwright image, --network host, loopback server only)
IMAGE   ?= camper-trailer:0.1
PORT    ?= 8791
UIDGID  := $(shell id -u):$(shell id -g)
GIT_REV := $(shell git rev-parse --short HEAD 2>/dev/null || echo uncommitted)
DOCKER  := docker run --rm --user $(UIDGID) -e HOME=/work/.home -e ASTRO_TELEMETRY_DISABLED=1 -e npm_config_cache=/work/.home/.npm -e GIT_REV=$(GIT_REV) -e SITE_URL -e SITE_BASE -v $(CURDIR):/work -w /work $(IMAGE)
T       := timeout

.PHONY: all image data model trailer ute check strict drawings site serve shots clean

all: image data model ute trailer check drawings site
	@cat build/checks/summary.txt

image:
	@docker image inspect $(IMAGE) >/dev/null 2>&1 || $(T) 1200 docker build -t $(IMAGE) docker

data: image
	$(T) 300 $(DOCKER) python -m cad.build data

model: data
	$(T) 1200 $(DOCKER) python -m cad.build model

# the trailer's jack-knife and GCM checks read the ute's model (build/ute/ute.json), so the ute builds first
ute: model
	$(T) 1200 $(DOCKER) python -m cad.build ute

trailer: ute
	$(T) 1200 $(DOCKER) python -m cad.build trailer

# pytest measures every check on the B-rep model and writes build/checks/checks.json.
# Its exit code is recorded, not propagated, so a failing check shows on the site instead of hiding it.
check: trailer ute
	@mkdir -p build/checks
	-$(T) 1200 $(DOCKER) sh -c 'python -m pytest cad/tests -p no:cacheprovider -rxXf --junitxml=build/checks/junit.xml > build/checks/pytest.log 2>&1; echo $$? > build/checks/pytest.exit'
	@tail -n 40 build/checks/pytest.log
	@printf 'pytest exit code %s: %s\n' "$$(cat build/checks/pytest.exit)" "$$(tail -n 1 build/checks/pytest.log)" > build/checks/summary.txt

strict: all
	@test "$$(cat build/checks/pytest.exit)" = "0" || (echo "design checks failed"; exit 1)

drawings: check
	$(T) 1800 $(DOCKER) python -m cad.build drawings

site: drawings check
	$(T) 300 $(DOCKER) python -m cad.sitedata
	$(T) 900 $(DOCKER) sh -c 'cd site && (test -d node_modules || npm ci --no-audit --no-fund --registry=https://registry.npmjs.org/) && npx astro build'

serve:
	$(T) 3600 python3 -m http.server $(PORT) --bind 127.0.0.1 --directory site/dist

shots:
	$(T) 600 docker run --rm --network host --shm-size=1g --user $(UIDGID) -e HOME=/work/.home -e npm_config_cache=/work/.home/.npm \
	  -v $(CURDIR):/work -w /work/shot mcr.microsoft.com/playwright:v1.63.0-noble \
	  sh -c '(test -d node_modules || npm i --no-audit --no-fund --registry=https://registry.npmjs.org/ playwright@1.63.0) && node shot.mjs $(PORT) && node scroll-check.mjs $(PORT)'

clean:
	rm -rf build site/dist site/.astro site/public/models site/public/downloads site/public/drawings \
	  site/src/data/generated site/src/content/docs/steps site/src/content/docs/research
