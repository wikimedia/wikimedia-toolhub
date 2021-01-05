<template>
	<v-container>
		<v-row>
			<v-col cols="12">
				<h2 class="display-1">
					{{ $t( 'auditlogs' ) }}
				</h2>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="py-0">
				<p>{{ $t( 'auditlogs-pagetitle' ) }}</p>
			</v-col>
		</v-row>

		<v-row v-if="apiErrorMsg">
			<v-col cols="12">
				<v-alert
					border="left"
					type="error"
					elevation="2"
					width="100%"
				>
					{{ $t( 'apierror' ) }} {{ apiErrorMsg }}
				</v-alert>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<dl v-for="log in auditLogs"
					:key="log.id"
					class="row elevation-2 ma-1 mb-2 pa-4"
				>
					<dd class="me-1">
						<v-icon
							v-if="log.action === 'created'"
							size="20"
							class="mb-1"
						>
							mdi-note-plus-outline
						</v-icon>

						<v-icon
							v-if="log.action === 'updated'"
							size="20"
							class="mb-1"
						>
							mdi-update
						</v-icon>

						<v-icon
							v-if="log.action === 'deleted'"
							size="20"
							class="mb-1"
						>
							mdi-delete-outline
						</v-icon>
					</dd>

					<dd class="me-1">
						<template
							v-if="$vuetify.rtl"
						>
							{{ log.timestamp | moment( "h:mm, DD &#x202b;MMMM&#x202c; YYYY" ) }}
						</template>
						<template
							v-else
						>
							{{ log.timestamp | moment( "h:mm, DD MMMM YYYY" ) }}
						</template>
					</dd>

					<dd class="me-1">
						<template
							v-if="log.user"
						>
							<a :href="`http://meta.wikimedia.org/wiki/User:${log.user.username}`" target="_blank">{{ log.user.username
							}}</a>
						</template>
						<template
							v-else
						>
							{{ $t( 'system-user' ) }}
						</template>
					</dd>

					<dd class="me-1">
						<template
							v-if="log.user"
						>
							(<a :href="`http://meta.wikimedia.org/wiki/User_talk:${log.user.username}`"
								target="_blank"
							>{{ $t( 'talk' ) }}</a>)
						</template>
					</dd>

					<dd class="me-1">
						{{ $t( 'auditlog-summary',
							{
								action: log.action,
								target: log.target.type
							}
						) }}
					</dd>

					<dd class="me-1">
						<template
							v-if="log.target.type === 'tool'"
						>
							"<a
								:href="`/tool/${log.target.id}`"
								target="_blank"
							>{{ log.target.label }}</a>"
						</template>

						<template
							v-else-if="log.target.type === 'url'"
						>
							"<a
								:href="`${log.target.label}`"
								target="_blank"
							>{{ log.target.label }}</a>"
						</template>

						<template
							v-else-if="log.target.type === 'user'"
						>
							"{{ log.target.label }}"
						</template>
					</dd>

					<dd class="me-1">
						<template
							v-if="log.message"
						>
							({{ log.message }})
						</template>
					</dd>
				</dl>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<v-pagination
					v-if="numLogs > 0"
					v-model="page"
					:length="Math.ceil( numLogs / itemsPerPage )"
					class="ma-4"
					total-visible="5"
					@input="goToPage"
				/>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';

export default {
	data() {
		return {
			page: 1,
			itemsPerPage: 10
		};
	},
	computed: {
		...mapState( 'auditlogs', [ 'auditLogs', 'apiErrorMsg', 'numLogs' ] )
	},
	methods: {
		fetchAuditLogs() {
			this.$store.dispatch( 'auditlogs/fetchAuditLogs', this.page );
		},
		goToPage( page ) {
			this.page = page;
			this.fetchAuditLogs();
		}
	},
	mounted() {
		this.fetchAuditLogs();
	}
};
</script>
