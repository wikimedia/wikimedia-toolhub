<template>
	<v-container v-if="list">
		<v-app-bar
			v-if="!revId"
			color="base100"
			dense
			flat
			class="list-app-bar"
		>
			<v-spacer />
			<v-btn
				v-if="$can( 'change', list )"
				:to="{ name: 'lists-edit', params: { id: list.id } }"
				color="primary base100--text"
				:small="$vuetify.breakpoint.smAndDown"
			>
				<v-icon class="me-2">
					mdi-pencil
				</v-icon>
				{{ $t( 'lists-editlist' ) }}
			</v-btn>

			<v-btn
				v-if="$can( 'delete', list )"
				:small="$vuetify.breakpoint.smAndDown"
				class="ms-4"
				color="error"
				@click="confirmDeleteDialog = true"
			>
				<v-icon class="me-2">
					mdi-delete
				</v-icon>
				{{ $t( 'delete' ) }}
			</v-btn>
			<FeatureButton v-if="list.published" :list="list" />
			<v-btn
				:to="{ name: 'lists-history', params: { id: list.id } }"
				:small="$vuetify.breakpoint.smAndDown"
				class="ms-4"
			>
				<v-icon class="me-2">
					mdi-history
				</v-icon>
				{{ $t( 'viewhistory' ) }}
			</v-btn>
		</v-app-bar>
		<v-card
			elevation="0"
			class="list-card__card"
		>
			<v-card-title class="px-0">
				<CommonsImage
					:commons-url="list.icon"
					:size="50"
					class="me-2"
				/>
				<h2 class="list-card__title text-h4 me-2">
					{{ list.title }}
				</h2>
				<v-chip
					v-if="list.featured"
					color="yellow30"
					text-color="base100"
					:small="$vuetify.breakpoint.smAndDown"
				>
					<v-icon size="15" class="me-1">
						mdi-star
					</v-icon>
					{{ $t( 'listinfo-featuredlist' ) }}
				</v-chip>
			</v-card-title>
			<v-card-text>
				<v-row>
					<v-col cols="12" class="px-0">
						<div
							class="text--primary text-subtitle-1"
							dir="auto"
						>
							{{ list.description }}
						</div>
					</v-col>
				</v-row>

				<v-row>
					<v-col
						lg="2"
						md="6"
						cols="12"
					>
						<dl class="list-card__authors row pt-1 text-subtitle-1">
							<dt class="me-1">{{ $t( 'authors' ) }}:</dt>
							<dd class="line-clamp">{{ list.created_by.username }}</dd>
						</dl>
					</v-col>

					<v-col md="6" cols="12">
						<dl class="row pt-1 text-subtitle-1">
							<dt class="me-1">{{ $t( 'datecreated' ) }}:</dt>
							<dd>{{ list.created_date | moment( 'lll' ) }}</dd>
						</dl>
					</v-col>

					<v-col
						lg="4"
						md="12"
						cols="12"
						class="py-1 px-0 text-md-end"
					>
						<v-btn
							text
							transparent
							color="primary"
							:small="$vuetify.breakpoint.smAndDown"
							@click="copyToClipboard"
						>
							<v-icon class="me-2">
								mdi-link-variant
							</v-icon>
							{{ $t( 'listinfo-copylink' ) }}
						</v-btn>
					</v-col>
				</v-row>

				<v-row v-if="showClipboardMsg">
					<v-col class="py-1 px-0 text-md-end">
						{{ $t( 'copiedtoclipboard' ) }}
					</v-col>
				</v-row>
			</v-card-text>
		</v-card>

		<v-divider />

		<v-row class="my-2">
			<v-col v-for="tool in list.tools"
				:key="tool.name"
				class="lists pa-0"
			>
				<v-card
					class="ma-4"
					min-width="210"
				>
					<ToolCard :tool="tool" />
				</v-card>
			</v-col>
		</v-row>

		<ConfirmDeleteDialog v-if="list.id"
			v-model="confirmDeleteDialog"
			@delete="deleteList"
		/>
	</v-container>
</template>

<script>
import CommonsImage from '@/components/common/CommonsImage';
import FeatureButton from '@/components/lists/FeatureButton';
import ToolCard from '@/components/tools/ToolCard';
import ConfirmDeleteDialog from '@/components/common/ConfirmDeleteDialog';

export default {
	name: 'ListInfo',
	components: {
		CommonsImage,
		FeatureButton,
		ToolCard,
		ConfirmDeleteDialog

	},
	props: {
		list: {
			type: Object,
			default: null
		},
		revId: {
			type: [ String, Number ],
			default: null
		},
		showClipboardMsg: {
			type: Boolean
		}
	},
	data() {
		return {
			confirmDeleteDialog: false
		};
	},
	methods: {
		copyToClipboard() {
			this.$emit( 'copy-to-clipboard' );
		},
		deleteList() {
			this.$emit( 'delete-list' );
			this.confirmDeleteDialog = false;
		}
	}
};
</script>
