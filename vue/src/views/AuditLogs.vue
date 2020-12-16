<template>
	<v-container>
		<v-row>
			<v-col cols="12"
				class="pa-0 mt-2"
			>
				<h2 class="display-1">
					{{ $t( 'auditlogs' ) }}
				</h2>
			</v-col>

			<v-col cols="12"
				class="pa-0 mt-2"
			>
				<p>{{ $t( 'auditlogs-pagetitle' ) }}</p>
			</v-col>

			<v-col lg="6"
				cols="12"
				class="pa-0"
			>
				<v-alert
					v-if="apiErrorMsg"
					border="left"
					type="error"
					elevation="2"
					width="100%"
				>
					{{ $t( 'apierror' ) }} {{ apiErrorMsg }}
				</v-alert>
			</v-col>

			<v-col lg="8" cols="12">
				<v-row v-for="log in auditLogs"
					:key="log.id"
					class="elevation-2 mt-2 pa-1"
				>
					<v-col>
						<v-icon
							v-if="log.action === 'create'"
							size="20"
							class="mb-1"
						>
							mdi-note-plus-outline
						</v-icon>

						<v-icon
							v-if="log.action === 'update'"
							size="20"
							class="mb-1"
						>
							mdi-update
						</v-icon>

						<v-icon
							v-if="log.action === 'delete'"
							size="20"
							class="mb-1"
						>
							mdi-delete-outline
						</v-icon>

						..
						{{ log.timestamp | moment( "DD MMMM YYYY, h:mm" ) }}

						..
						<template
							v-if="log.user"
						>
							<a :href="`http://meta.wikimedia.org/wiki/User:${log.user.username}`" target="_blank">{{ log.user.username
							}}</a>
							(<a :href="`http://meta.wikimedia.org/wiki/User_talk:${log.user.username}`"
								target="_blank"
							>{{ $t( 'talk' ) }}</a>)
						</template>
						<template
							v-else
						>
							{{ $t( 'system-user' ) }}
						</template>
						..
						{{ $t( 'auditlog-summary',
							{
								action: log.action,
								target: log.target.type
							}
						) }}

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

						<template
							v-if="log.message"
						>
							..
							({{ log.message }})
						</template>
					</v-col>
				</v-row>
			</v-col>

			<v-col lg="8" cols="12">
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
