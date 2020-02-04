import requests

def main():
    url ='https://jobs.github.com/positions.json'
    request = requests.get(url)

    print(request.status_code)
    page_response = request.json()

    #empty list to store dictionaries
    response_dict = []
    search_jobs(page_response)

def search_jobs(page_response):
    for job_listings in page_response[:30]:
        url = "https://jobs.github.com/positions?page={}.json".format(job_listings)
        request = requests.get(url)
        print("id: {}\tstatus: {}".format(job_listings, request.status_code))

main()
#this was supposed to write/save the info to a jobListing text file
def save_file(request):
    file = open("jobListing.txt")
    for i in range(200):
        file.write(request)
    save_file()
    save_file(request)
