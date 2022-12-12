<template>
	<v-app>
		<v-app-bar
			app
			color="primary"
			flat
			tile
			:clipped-left="$vuetify.breakpoint.mdAndUp && !$vuetify.rtl"
			:clipped-right="$vuetify.breakpoint.mdAndUp && $vuetify.rtl"
		>
			<v-app-bar-nav-icon
				v-if="$vuetify.breakpoint.smAndDown"
				dark
				@click.stop="drawer = !drawer"
			/>
			<template
				v-if="$vuetify.breakpoint.mdAndUp"
			>
				<router-link to="/">
					<v-img
						class="me-2"
						src="/static/img/logo-solid-white.svg"
						alt="Toolforge logo"
						width="35"
						height="35"
						contain
					/>
				</router-link>
				<router-link to="/">
					<v-toolbar-title
						class="text-h4 white--text"
					>
						{{ $t( 'toolhub' ) }}
					</v-toolbar-title>
				</router-link>
			</template>
			<v-spacer />
			<template v-if="$vuetify.breakpoint.smAndUp">
				<SearchBar
					target="tool"
					@search="onSearchBarSearch"
				/>
				<v-spacer />
			</template>
			<SelectLocale />
			<UserStatus />
			<template
				v-if="$vuetify.breakpoint.xs"
				#extension
			>
				<SearchBar
					class="mb-2"
					target="tool"
					@search="onSearchBarSearch"
				/>
			</template>
		</v-app-bar>

		<v-navigation-drawer
			v-model="drawer"
			class="navbar"
			app
			color="secondary"
			dark
			floating
			clipped
			:permanent="$vuetify.breakpoint.mdAndUp"
			:expand-on-hover="$vuetify.breakpoint.mdAndUp && drawer && !prefersReducedMotion"
			:right="$vuetify.rtl"
		>
			<template
				v-if="$vuetify.breakpoint.smAndDown"
			>
				<v-list-item class="ms-2 mt-1 ps-1">
					<router-link to="/">
						<v-img
							src="/static/img/logo-solid-white.svg"
							alt="Toolforge logo"
							width="35"
							height="35"
							class="me-6"
						/>
					</router-link>
					<v-list-item-content class="mt-1">
						<v-list-item-title class="font-weight-bold">
							<router-link
								to="/"
								class="white--text text-decoration-none"
							>
								{{ $t( 'toolhub' ) }}
							</router-link>
						</v-list-item-title>
					</v-list-item-content>
					<v-btn
						v-if="$vuetify.breakpoint.smAndDown"
						icon
						@click.stop="drawer = !drawer"
					>
						<v-icon>mdi-chevron-left</v-icon>
					</v-btn>
				</v-list-item>
				<v-divider class="mt-2" />
			</template>
			<v-list
				dense
				nav
			>
				<v-list-item
					v-for="route in routes"
					:key="route.name"
					:to="route.path"
					link
					exact
				>
					<v-list-item-icon>
						<v-icon>{{ route.meta.icon }}</v-icon>
					</v-list-item-icon>
					<v-list-item-content>
						<!-- eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys -->
						<v-list-item-title>{{ $t( route.name ) }}</v-list-item-title>
					</v-list-item-content>
				</v-list-item>
			</v-list>

			<v-divider class="mt-2" />

			<v-list
				dense
				nav
			>
				<v-list-item
					v-for="link in footerLinks"
					:key="link.msg"
					:href="link.href"
					link
				>
					<v-list-item-icon>
						<v-icon>{{ link.icon }}</v-icon>
					</v-list-item-icon>
					<v-list-item-content>
						<!-- eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys -->
						<v-list-item-title>{{ $t( link.msg ) }}</v-list-item-title>
					</v-list-item-content>
				</v-list-item>
				<v-list-item
					:href="commitHref"
					link
				>
					<v-list-item-icon>
						<v-icon>mdi-git</v-icon>
					</v-list-item-icon>
					<v-list-item-content>
						<v-list-item-title>
							{{ $t( 'version-number', [ version, commitHash ] ) }}
						</v-list-item-title>
					</v-list-item-content>
				</v-list-item>
			</v-list>

			<v-divider class="mt-2" />
		</v-navigation-drawer>
		<v-main>
			<v-container fluid>
				<v-alert
					v-if="config.isDemo"
					dismissible
					prominent
					text
					type="info"
				>
					{{ $t( 'demo-server-notice' ) }}
				</v-alert>
				<router-view />
			</v-container>
			<Notifications />
		</v-main>
		<v-footer app>
			<v-col
				class="py-0 text-center text-caption"
				cols="12"
			>
				<I18nHtml msg="footer-content-license">
					<a
						href="https://creativecommons.org/publicdomain/zero/1.0/"
						target="_blank"
					>{{ $t( 'link-cc0' ) }}</a>
				</I18nHtml>
			</v-col>
		</v-footer>
	</v-app>
</template>

<script>
import { EventBus } from '@/helpers/event-bus';

import I18nHtml from '@/components/common/I18nHtml';
import SearchBar from '@/components/search/SearchBar';
import SelectLocale from '@/components/locale/SelectLocale';
import UserStatus from '@/components/user/Status';

export default {
	components: {
		I18nHtml,
		SearchBar,
		SelectLocale,
		UserStatus
	},
	data() {
		return {
			commitHash: process.env.VUE_APP_GIT_HASH,
			drawer: false,
			footerLinks: [
				{
					icon: 'mdi-security',
					msg: 'link-privacy-policy',
					href: 'https://foundation.wikimedia.org/wiki/Special:MyLanguage/Privacy_policy'
				},
				{
					icon: 'mdi-book-check-outline',
					msg: 'link-tou',
					href: 'https://foundation.wikimedia.org/wiki/Special:MyLanguage/Terms_of_Use'
				},
				{
					icon: 'mdi-police-badge-outline',
					msg: 'link-coc',
					href: 'https://www.mediawiki.org/wiki/Special:MyLanguage/Code_of_Conduct'
				},
				{
					icon: 'mdi-code-tags',
					msg: 'link-vcs',
					href: 'https://gerrit.wikimedia.org/r/plugins/gitiles/wikimedia/toolhub/+/refs/heads/main'
				},
				{
					icon: 'mdi-bug',
					msg: 'link-issues',
					href: 'https://phabricator.wikimedia.org/tag/toolhub/'
				},
				{
					icon: 'mdi-file-document-multiple-outline',
					msg: 'link-docs',
					href: 'https://meta.wikimedia.org/wiki/Toolhub'
				}
			],
			prefersReducedMotion: window.matchMedia( '(prefers-reduced-motion: reduce)' ).matches,
			vcsLink: 'https://gerrit.wikimedia.org/g/wikimedia/toolhub/+/',
			version: process.env.VUE_APP_VERSION
		};
	},
	computed: {
		routes() {
			return this.$router.options.routes.filter(
				( route ) => ( route.meta !== undefined )
			);
		},
		commitHref() {
			return this.vcsLink + this.commitHash;
		},
		config() {
			return JSON.parse(
				document.getElementById( 'toolhub-config' ).textContent
			);
		}
	},
	methods: {
		onSearchBarSearch( query ) {
			if ( this.$route.name === 'search' ) {
				// Currently on the search page
				EventBus.$emit( 'toolSearch', query );
			} else {
				// Navigate to the search page
				this.$router.push( {
					name: 'search',
					query: { q: query }
				} );
			}
		}
	},
	created() {
		this.$store.dispatch( 'user/getUserInfo' ).then( () => {
			this.$store.dispatch( 'locale/initializeLocale', { vm: this } );
		} );
	}
};
</script>
