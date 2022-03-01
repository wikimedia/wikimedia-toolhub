<template>
	<div v-frag>
		<v-text-field
			v-if="widget === 'text'"
			v-model="model"
			:required="ui.required"
			:rules="validationRules"
			:prepend-icon="ui.icon"
			:hint="schema.description"
			:counter="schema.maxLength"
			clearable
		>
			<template #label>
				<InputLabel :label="ui.label" :required="ui.required" />
			</template>
		</v-text-field>
		<v-textarea
			v-else-if="widget === 'multiline'"
			v-model="model"
			:required="ui.required"
			:rules="validationRules"
			:prepend-icon="ui.icon"
			:hint="schema.description"
			:counter="schema.maxLength"
			rows="1"
			auto-grow
			clearable
		>
			<template #label>
				<InputLabel :label="ui.label" :required="ui.required" />
			</template>
		</v-textarea>
		<v-autocomplete
			v-else-if="widget === 'select'"
			v-model="model"
			:label="ui.label"
			:rules="validationRules"
			:prepend-icon="ui.icon"
			:hint="schema.description"
			:items="ui.select.items()"
			:multiple="ui.multiple || false"
			:deletable-chips="ui.multiple || false"
			:small-chips="ui.multiple || false"
			:clearable="ui.multiple ? false : true"
		>
			<template #label>
				<InputLabel :label="ui.label" :required="ui.required" />
			</template>
		</v-autocomplete>
		<v-combobox
			v-else-if="widget === 'multi-select'"
			v-model="model"
			:rules="validationRules"
			:prepend-icon="ui.icon"
			:hint="schema.description"
			multiple
			deletable-chips
			small-chips
		>
			<template #label>
				<InputLabel :label="ui.label" :required="ui.required" />
			</template>
		</v-combobox>
		<v-combobox
			v-else-if="widget === 'multi-select-tool'"
			v-model="model"
			:loading="toolAutoCompleteLoading"
			:search-input.sync="toolAutoComplete"
			:menu-props="menuProps"
			:items="getToolAutoCompleteResultsArr()"
			:rules="validationRules"
			:prepend-icon="ui.icon"
			:hint="schema.description"
			hide-selected
			multiple
			deletable-chips
			small-chips
		>
			<template #label>
				<InputLabel :label="ui.label" :required="ui.required" />
			</template>
			<template #item="data">
				<v-list-item-content>
					<v-list-item-title>
						<dl class="row ma-0">
							<dt class="me-1">{{ toolAutoCompleteResults[data.item][0] }}</dt>
							<dd>({{ toolAutoCompleteResults[data.item][1] }})</dd>
						</dl>
					</v-list-item-title>
				</v-list-item-content>
			</template>

			<template v-if="!toolAutoCompleteLoading" #no-data>
				<v-list-item>
					<v-list-item-content>
						<v-list-item-title>
							{{ $t( 'tool-not-found', [ toolAutoComplete ] ) }}
						</v-list-item-title>
					</v-list-item-content>
				</v-list-item>
			</template>
		</v-combobox>
		<template v-else-if="widget === 'authors'">
			<v-combobox
				v-model="model"
				:hint="schema.description"
				:prepend-icon="ui.icon"
				:append-icon="ui.appendIcon"
				multiple
				readonly
				@click:append="showAuthorDialog( null )"
				@click="showAuthorDialog( null )"
			>
				<template #label>
					<InputLabel :label="ui.label" :required="ui.required" />
				</template>
				<template #selection="{ item, parent }">
					<v-chip
						class="ma-2"
						close
						@click:close="parent.selectItem( item )"
						@click="showAuthorDialog( item )"
					>
						{{ item.name }}
					</v-chip>
				</template>
			</v-combobox>
			<AuthorDialog
				:ui-schema="ui.items"
				:schema="schema.items"
				:authors.sync="model"
				:author-edit.sync="authorEdit"
			/>
		</template>
		<v-checkbox
			v-else-if="widget === 'checkbox'"
			v-model="model"
		>
			<template #label>
				<InputLabel :label="ui.label" :required="ui.required" />
			</template>
		</v-checkbox>
		<template v-else-if="widget === 'array'">
			<v-row
				v-for="( obj, idx ) in value"
				:key="idx"
			>
				<v-col sm="11"
					cols="10"
				>
					<InputWidget
						v-model="model[ idx ]"
						:schema="schema.items"
						:ui-schema="ui.items"
					/>
				</v-col>

				<template
					v-if="ui.items.widget === 'url-multilingual'"
				>
					<v-col v-if="idx === 0"
						sm="1"
						cols="2"
					>
						<v-btn
							elevation="2"
							icon
							class="mt-2"
							color="primary base100--text"
							@click="alterArray( 'add', value )"
						>
							<v-icon>
								mdi-plus
							</v-icon>
						</v-btn>
					</v-col>

					<v-col v-else
						sm="1"
						cols="2"
					>
						<v-btn
							elevation="2"
							icon
							class="mt-2"
							color="error"
							@click="alterArray( 'remove', value, idx )"
						>
							<v-icon>
								mdi-minus
							</v-icon>
						</v-btn>
					</v-col>
				</template>
			</v-row>
		</template>
		<template v-else-if="widget === 'url-multilingual'">
			<v-col cols="12">
				<InputWidget
					v-model="model.url"
					:schema="schema.properties.url"
					:ui-schema="ui.url"
				/>
			</v-col>
			<v-col cols="12">
				<InputWidget
					v-model="model.language"
					:schema="schema.properties.language"
					:ui-schema="ui.language"
				/>
			</v-col>
		</template>
		<pre v-else>
			{{ schema }}
		</pre>
	</div>
</template>

<script>
import { mapState } from 'vuex';
import patternRegexRule from '@/plugins/pattern-regex';
import InputLabel from '@/components/common/InputLabel';
import { isValidHttpUrl } from '@/helpers/validation';

export const methods = {
	/**
	 * Initialize our model based on our value and schema.
	 */
	initModel() {
		if ( this.value ) {
			if (
				this.schema.type === 'object' &&
				Object.keys( this.value ).length > 0
			) {
				this.model = this.value;
			} else if (
				this.schema.type === 'array' &&
				this.value.length > 0
			) {
				this.model = this.value;
			} else if (
				this.schema.type === 'boolean' &&
				this.value !== null
			) {
				this.model = this.value;
			} else if (
				this.schema.type === 'string' ||
				this.schema.type === 'number' ||
				this.schema.type === 'integer'
			) {
				this.model = this.value;
			} else {
				this.model = this.initBlankValue();
			}
		} else {
			this.model = this.initBlankValue();
		}
	},

	initBlankValue() {
		switch ( this.schema.type ) {
			case 'object':
				return {};
			case 'array':
				return [];
			case 'boolean':
				return false;
			case 'number':
			case 'integer':
			default:
				return null;
		}
	},

	/**
	 * Grow/shrink an array type.
	 *
	 * @param {string} op - operation to perform ('add' or 'remove')
	 * @param {Array} data - Array to modify
	 * @param {number?} index - Index of item to remove
	 */
	alterArray( op, data, index ) {
		if ( op === 'remove' ) {
			if ( data.length > 1 ) {
				data.splice( index, 1 );
			}
		} else if ( op === 'add' ) {
			// TODO: make this configurable
			data.push( { url: '', language: this.$i18n.locale } );
		}
	},
	performToolAutoComplete( v ) {
		this.toolAutoCompleteLoading = true;
		this.$store.dispatch( 'search/autoCompleteTools', v ).finally(
			() => {
				this.toolAutoCompleteLoading = false;
			}
		);
	},
	getToolAutoCompleteResultsArr() {
		return this.toolAutoCompleteResults ?
			Object.keys( this.toolAutoCompleteResults ) :
			[];
	},
	/**
	 * Populate and open the AuthorDialog.
	 *
	 * @param {?Object} author - Author information to display
	 */
	showAuthorDialog( author ) {
		this.authorEdit.author = author;
		this.authorEdit.authorDialogOpen = true;
	}
};

export default {
	name: 'InputWidget',
	components: {
		InputLabel,
		// Import via function to work around circular dependency between
		// AuthorDialog and InputWidget components.
		AuthorDialog: () => import( '@/components/common/AuthorDialog' )
	},
	props: {
		schema: {
			type: Object,
			default: () => {},
			required: true
		},
		uiSchema: {
			type: Object,
			default: () => {}
		},
		value: {
			type: [ String, Number, Boolean, Array, Object ],
			default: null
		}
	},
	data: () => ( {
		model: null,
		toolAutoCompleteLoading: false,
		authorEdit: {
			author: null,
			authorDialogOpen: false
		},
		toolAutoComplete: null
	} ),
	computed: {
		/**
		 * Get our UI helper data.
		 *
		 * @return {Object}
		 */
		ui() {
			return this.schema[ 'x-ui' ] || this.uiSchema;
		},
		widget() {
			if ( this.ui.widget ) {
				return this.ui.widget;
			}
			if ( this.schema.type === 'string' ) {
				if ( this.schema.enum ) {
					return 'select';
				}
				return this.schema.maxLength > 2047 ? 'multiline' : 'text';
			}
			return this.schema.type;
		},
		menuProps() {
			return !this.toolAutoComplete ? { value: false } : {};
		},
		validationRules() {
			const schema = this.schema;
			const ui = this.ui;
			const rules = [];
			if ( schema.maxLength ) {
				rules.push(
					( v ) => ( v || '' ).length <= schema.maxLength ||
						this.$t( 'charslimit', [ schema.maxLength ] )
				);
			}
			if ( schema.pattern ) {
				rules.push( ...patternRegexRule( schema.pattern ) );
			}
			if ( schema.format === 'uri' ) {
				rules.push(
					( v ) => !v ? true : isValidHttpUrl( v ) ||
					this.$t( 'urlinvalid' )
				);
			}
			if ( ui.required === true ) {
				rules.push( ( v ) => !!v || this.$t( 'required-field' ) );
			}
			return rules;
		},
		...mapState( 'search', {
			toolAutoCompleteResults: 'toolAutoCompleteResults'
		} )
	},
	methods,
	watch: {
		toolAutoComplete: {
			handler( val ) {
				if ( val && val !== this.model ) {
					this.performToolAutoComplete( val );
				}
			}
		},
		model: {
			handler( newVal ) {
				this.$emit( 'input', newVal );
			},
			deep: true,
			immediate: true
		},
		value: {
			handler( newVal, oldVal ) {
				if ( JSON.stringify( oldVal ) !== JSON.stringify( newVal ) ) {
					this.initModel();
				}
			},
			deep: true
		}
	},
	created() {
		this.initModel();
	}
};
</script>
