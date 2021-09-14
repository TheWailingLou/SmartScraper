# SmartScraper
This is a web scraper powered by selenium and Detectron 2 with fully configurable search and scrape criteria. Currently this is using the LVIS model, but other models will be added in the future.

## Setup
### Initial Setup
After cloning the repo, `pip install` all requirements in `requirements.txt`. You will also need to have Chrome installed, and a chromedriver with same version as your browser. You can [download the chrome driver here.](https://chromedriver.chromium.org/downloads) Once you have it downloaded, place the the driver in `SMART_SCRAPER_PATH/smart_search/scraper/chrome_driver`.

### Quick Setup
After following the initial setup, you can verify everything is working with `python /example.py`. This should open chrome and scrape 10 images of dogs, and place them into `/results/test/dog`. If it finds any images of cats it will also save them into `results/test/cat`. It may take some time to complete as it will analyze every image. For the complete setup guide, continue reading with configuration.

## Configuration
### SearchConfig
The search config is what controls the general format of the search. The default params do a decent job of exploring the surface, but for scraping a larger data set, there are many options to fine tune your search.

| Parameter   | Type | Description | Required | Default Value |
| ----------- | ----------- | ----------- | ----------- | ----------- |
| search_term | string | Term that is searched for via google. | Yes | n/a |
| images_to_scrape | int | Total quantity of images that match primary filter | Yes | n/a |
| batch_size |int | quantity of images to analyze before redirecting. For larger scrapes, 30-40 is a good quantity | No | 5 |
| max_depth | int |total number of redirects before search fails if it hasn't hit number specified in `images_to_scrape`. | No | 5 |
| site | string |searches for images from a specific site. i.e. "https://www.instagram.com/" would only search images from instagram. An empty string is ignored | No | "" |
| allowed_reanalysis_count |int | When this number is hit, a redirect will occur, even if it is less than the batch size. Usefull if repeating similar searches | No | math.inf |
| close_browser_when_done |bool | If browser should automatically close when complete | No | True |
| headless_browsing | bool |If browser should display in chrome or run headless | No | False |
| side_panel_max_depth |int | clicking on a side panel image results in a different set of side panel images. This specifies how many times to do this | No | 3 |
| side_panel_max_siblings_to_check |int | side panels have around 12 images. A sibling is considered two images that appear in the same side panel | No | 4 |
| root_checks_before_side_dive |int | before analyzing images in side panels, will analyze this quantity of top level images | No | 4 |


### Filters and Filter Rules
A filter is a set of filter rules that act as a gatekeeper for wether an image should or should not be saved. When an image is classified, it will look at each filter rule and if all verifications pass the image is saved.

Filter Rule:

| Parameter   | Type | Description | Required | Default Value |
| ----------- | ---- | ----------- | -------- | ------------- |
| category | string | A category name to filter off of. Because currently this uses the LVIS model, any specified category must be an LVIS recognized object. You can see choices [here](https://www.lvisdataset.org/explore) | Yes | n/a |
| comparator | string | Allowed values are ">", "<", ">=", "<=", "=". Comparator here is applied to the score. When filtering, the images score for a category will be compared using this on the required score.  | Yes | n/a |
| autoscore | double | If an object is not found this score will automatically be applied. 0 is strongly recommended | No | 0. |
| q_compare | string | Same allowed values as comparator. This is looking at the quantity found rather than the score, and is used in conjunction with expected_quantity | No | ">=" |
| expected_quantity | int | expected quantity to be in the image with q_compare. E.g. if looking for images with two of something instead of one, set this to 2 | No | 1 |

Example for filter rule:
```
spectacle_filter = FilterRule("spectacles", ">", 0.5, q_compare='>=', expected_quantity=1)
# Verify that spectacles score is greater than 0.5, and there is at least 1 instance of spectacles.
shoe_filter = FilterRule("shoe", ">=", 0.7, q_compare='>=', expected_quantity=2)
# Verify that score for a shoe is at least 0.7, and there are at least 2 instances of shoes.
```

Example for filter:
```
shoe_and_spectacle_filter = ClassificationFilter({
    spectacle_filter,
    shoe_filter
  })
# verify conditions in both shoe and spectacle filter match.
```

### Prioritization
Prioritization affects the redirect aspects of the search. It prioritizes the rules in sequential order. If the first priority is hit then it will take the highest score of the first priority. If it is not, then it will check the second, etc. If no priority is hit, then on redirect it will select randomly.

PrioritzationRule:
| Parameter   | Type | Description | Required | Default Value |
| ----------- | ---- | ----------- | -------- | ------------- |
| category | string | A category name from the LVIS dataset. You can see choices [here](https://www.lvisdataset.org/explore) | Yes | n/a |
| value_definition | string | Must be either "highest" or "lowest" | No | "highest" |

Example:
```
dog_priority = PrioritizationRule("dog", "highest")
# from analyzed images, select image with highest score for dog.
cat_priority = PrioritizationRule("cat", "lowest")
# from analyzed images, select image with lowest score for cat.

prioritization = [
  dog_priority,
  cat_priority
]
# if no images with a score for dog are found, the image with lowest score for cat will be selected. If no images for cat are found, an image will be randomly selected.
```


### ClassificationBundle
A classification bundle is a set of rules and a bucket path for where to store images that meet those rules.

ClassificationBundle:

| Parameter   | Type | Description | Required | Default Value |
| ----------- | ---- | ----------- | -------- | ------------- |
| filter | ClassificationFilter | see filters above | Yes | n/a |
| name | string | a name for the image type | Yes | n/a |
| persist_out_path | string | a full path to the save location of images that match the filter | Yes | n/a |

## Tying it all together
The search method from `find.py` is an interface that combines a search config, a list of classificaton bundles, and a prioritization to find images and intelligently redirect to find more like images.

search:

| Parameter   | Type | Description | Required | Default Value |
| ----------- | ---- | ----------- | -------- | ------------- |
| search_config | SearchConfig | see SearchConfig above | yes | n/a |
| prioritization_rules | List<PrioritzationRule> | see prioritization above | yes | n/a |
| classification_bundles | List<ClassificationBundle> | see ClassificationBundle above | yes | n/a |

To see this all in action, look at `example.py`.
