<template>
	<v-app>
		<v-app-bar
			app
			color="primary"
			dark
			flat
			tile
		>
			<v-app-bar-nav-icon
				v-if="$vuetify.breakpoint.smAndDown"
				@click.stop="drawer = !drawer"
			/>

			<v-spacer />
			<SelectLocale />
			<UserStatus />
		</v-app-bar>

		<v-navigation-drawer
			v-model="drawer"
			app
			color="secondary"
			dark
			:floating="true"
			:permanent="$vuetify.breakpoint.mdAndUp"
			:expand-on-hover="$vuetify.breakpoint.mdAndUp && drawer"
			:right="$vuetify.rtl"
		>
			<v-list-item class="ms-2 mt-1 ps-1">
				<v-list-item-avatar
					size="35"
					class="me-4"
				>
					<v-img
						src="/static/img/logo-solid-white.svg"
						alt="Toolforge logo"
					/>
				</v-list-item-avatar>

				<v-list-item-content class="mt-1">
					<v-list-item-title class="font-weight-bold">
						{{ $t( 'toolhub' ) }}
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
import { mapState } from 'vuex';
import UserStatus from '@/components/user/Status';
import SelectLocale from '@/components/locale/SelectLocale';
import I18nHtml from '@/components/common/I18nHtml';

export default {
	components: {
		UserStatus,
		SelectLocale,
		I18nHtml
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
			vcsLink: 'https://gerrit.wikimedia.org/g/wikimedia/toolhub/+/',
			version: process.env.VUE_APP_VERSION
		};
	},
	computed: {
		...mapState( 'user', [] ),
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
	created() {
		this.$store.dispatch( 'user/getUserInfo', { vm: this } ).then( () => {
			this.$store.dispatch( 'locale/initializeLocale', { vm: this } );
		} );
	}
};
</script>
