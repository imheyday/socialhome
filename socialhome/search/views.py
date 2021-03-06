import xml

from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from federation.fetchers import retrieve_remote_profile
from federation.utils.text import validate_handle
from haystack.generic_views import SearchView
from whoosh.query import QueryError

from socialhome.content.models import Tag
from socialhome.content.utils import safe_text
from socialhome.enums import Visibility
from socialhome.users.models import Profile


class GlobalSearchView(SearchView):
    def get_queryset(self):
        """Exclude some information from the queryset.

        If logged in, exclude own profile and SELF+LIMITED profiles
        If not logged in, exclude all but PUBLIC profiles

        We exclude SELF profiles too, though they should never even be indexed.
        """
        queryset = super().get_queryset()
        return self.filter_queryset(queryset)

    def get(self, request, *args, **kwargs):
        """See if we have a direct match. If so redirect, if not, search.

        Try fetching a remote profile if the search term is a handle.
        """
        q = safe_text(request.GET.get("q"))
        if q:
            q = q.strip().lower()
        # Check if direct tag matches
        if q.startswith('#'):
            try:
                tag = Tag.objects.filter(
                    name=q[1:]
                ).annotate(
                    content_count=Count('contents')
                ).filter(
                    content_count__gt=0
                ).get()
            except Tag.DoesNotExist:
                pass
            else:
                return redirect(tag.get_absolute_url())
        # Check if profile matches
        if validate_handle(q):
            profile = None
            try:
                profile = Profile.objects.visible_for_user(request.user).get(handle=q)
            except Profile.DoesNotExist:
                # Try a remote search
                try:
                    remote_profile = retrieve_remote_profile(q)
                except (AttributeError, ValueError, xml.parsers.expat.ExpatError):
                    # Catch various errors parsing the remote profile
                    return super().get(request, *args, **kwargs)
                if remote_profile:
                    profile = Profile.from_remote_profile(remote_profile)
            if profile:
                return redirect(reverse("users:profile-detail", kwargs={"guid": profile.guid}))
        try:
            return super().get(request, *args, **kwargs)
        except QueryError:
            # Re-render the form
            messages.warning(self.request, _("Search string is invalid, please try another one."))
            return HttpResponseRedirect(self.get_success_url())


    def filter_queryset(self, queryset):
        """Do some of our own filtering on the queryset before returning."""
        if self.request.user.is_authenticated:
            queryset = queryset.exclude(handle=self.request.user.profile.handle)
            if self.request.user.is_staff:
                return queryset
            else:
                # TODO: LIMITED profiles are excluded from searches even though the user might already be following
                # one of them. This is an unfortunate issue that should be tackled at some point, to allow searching for
                # LIMITED profiles that the user has a follow relationship with.
                return queryset.exclude(profile_visibility__in=[
                    Visibility.SELF.value, Visibility.LIMITED.value
                ])
        return queryset.exclude(profile_visibility__in=[
            Visibility.LIMITED.value, Visibility.SITE.value, Visibility.SELF.value
        ])
