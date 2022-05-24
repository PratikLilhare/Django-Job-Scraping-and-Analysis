from django.http import FileResponse, JsonResponse
from django.shortcuts import render

from indeed.utils import find_jobs_from


def show(request):
    # TO DO make plot regeneration working

    # plot = Plot.objects.filter(user_id=request.user.id).first()
    # if plot:
    #     if plot[0].figure:
    #         plot[0].figure.delete()
    # if plot:
    #     plot.delete()

    if request.method == "POST":
        job_title = request.POST["query"]
        job_list = find_jobs_from(request, "Indeed", job_title, "india", [
                                  "titles"], filename="results.csv")
        job_list["query"] = job_title
        return JsonResponse(job_list)

    return render(request, "home.html")


def plot_image(request):
    img = open('media/figures/'+request.user.username+'.png', 'rb')

    response = FileResponse(img)

    return response


