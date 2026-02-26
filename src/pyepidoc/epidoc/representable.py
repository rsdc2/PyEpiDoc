from __future__ import annotations
from functools import cached_property, reduce
from typing import Sequence
from pyepidoc.xml.xml_text import XmlText
from pyepidoc.xml.xml_element import (
    XmlComment, 
    XmlNode, 
    ProcessingInstruction
)

from pyepidoc.shared.namespaces import XMLNS, TEINS
from pyepidoc.shared.enums import RegTextType
from pyepidoc.shared.classes import Showable
from pyepidoc.tei.tei_element import TeiElement


class RepresentableElement(TeiElement, Showable):

    @property
    def abbr_elems(self) -> Sequence[RepresentableElement]:
        """
        Return all abbreviation elements as a |list| of |Element|.
        """

        return [RepresentableElement(abbr) 
                for abbr in self.get_desc('abbr')]
        
    @property
    def am_elems(self) -> Sequence[RepresentableElement]:
        """
        Returns a |list| of abbreviation marker elements <am>.
        See https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-am.html,
        last accessed 2023-04-13.
        """

        return [RepresentableElement(abbr) 
                for abbr in self.get_desc('am')]
    
    @property
    def expan_elems(self) -> Sequence[RepresentableElement]:
        """
        Return all abbreviation expansions (i.e. abbreviation + expansion) 
        as a |list| of |Element|.
        """

        return [RepresentableElement(expan) 
                for expan in self.get_desc('expan')]


    def deepcopy(self) -> RepresentableElement:
        return RepresentableElement(self._e.deepcopy())

    @property
    def elem_classes(self) -> dict[str, type[RepresentableElement]]:
        from .representable_classes import representable_classes
        return representable_classes

    @property
    def following_nodes_in_ab(self) -> list[XmlNode]:

        """
        Returns any following Element or Text nodes whose
        ancestor is an `<ab>`.
        """

        return self._e.xpath(
            'following::node()[ancestor::x:ab]', 
            namespaces={'x': TEINS}
        )

    @cached_property
    def form(self) -> str:
        """
        Returns the full form, including any abbreviation expansion.
        Compare @normalized_form
        """

        return self._e._clean_text(self._e.text_desc)

    @property
    def form_normalized(self) -> str:
        """
        Returns the normalized form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>, <surplus> and <del> elements
        """
        return self.normalized_form
    
    @property
    def leiden_form(self) -> str:
        """
        Returns the form per Leiden conventions, i.e. with
        abbreviations expanded with brackets
        """
        if self.representable_cls_inst is None:
            return self._e.text_desc
        if type(self.representable_cls_inst) is type(self):
            raise TypeError(f'Class {type(self)} must implement property `leiden_form`.')
        return self.representable_cls_inst.leiden_form

    @property
    def leiden_plus_form(self) -> str:
        """
        Returns the Leiden form, with 
        interpunts indicated by middle dot;
        line breaks are indicated with vertical bar '|'
        """

        def string_rep(n: XmlNode) -> str:
            """
            Get the string representation of the node, if it is 'g', 'lb', 'gap',
            otherwise return empty string.
            """
            ln = n.localname

            if isinstance(n, (XmlText, XmlComment, ProcessingInstruction)):
                return ''

            if ln in ['g', 'lb', 'gap']:
                return self.elem_classes[ln](n).leiden_form
            
            return ''

        def get_next_non_text(
                acc: list[XmlNode],
                node: XmlNode
            ) -> list[XmlNode]:

            if acc != []:
                last = acc[-1]

                if isinstance(last, XmlText):
                    if str(last).strip() not in ['', '·']:
                        return acc 
                
                if last.localname in ['lb', 'w', 'name', 'persName', 'roleName', 'num']:
                    return acc
            
            return acc + [node]

        if type(self.representable_cls_inst) is type(self):
            raise TypeError(f'Class {type(self)} must implement property `leiden_plus_form`.')
        
        preceding = reversed(self.preceding_nodes_in_ab)
        following = self.following_nodes_in_ab

        preceding_upto_text = reduce(get_next_non_text, preceding, list[XmlNode]())
        preceding_upto_text = list(reversed(preceding_upto_text))
        following_upto_text = reduce(get_next_non_text, following, list[XmlNode]())
        
        prec_text = ''.join(map(string_rep, preceding_upto_text))
        following_text = ''.join(map(string_rep, following_upto_text))

        return prec_text + self.leiden_form + following_text        

    @property
    def local_id(self) -> str | None:
        """
        Return `@n` id
        """
        return self.get_attr('n')
    
    @local_id.setter
    def local_id(self, value: str | None) -> None:
        if value is None:
            self._e.remove_attr('n')
        else:
            self._e.set_attr('n', value)

    @property
    def xml_id(self) -> str | None:
        """
        Returns value of the xml:id attribute in the XML file.
        """
        return self.get_attr('id', namespace=XMLNS)

    @xml_id.setter
    def xml_id(self, id_value: str | None) -> None:
        """
        Sets the value of the xml:id attribute in the XML file.
        """
        if id_value is None:
            self._e.remove_attr('id', namespace=XMLNS)
        else:
            self.set_attr('id', id_value, namespace=XMLNS)

    @property
    def preceding_nodes_in_ab(self) -> list[XmlNode]:

        """
        Returns any preceding |_Element| or 
        |_ElementUnicodeResult| whose ancestor is an edition.
        """

        return self._e.xpath(
            'preceding::node()[ancestor::x:ab]', 
            namespaces={'x': TEINS}
        )

    @cached_property
    def simple_lemmatized_edition_element(self) -> RepresentableElement:
        """
        Element for use in simple-lemmatized edition
        """
        t = type(self)
        elem = t(self.deepcopy()._e)
        elem._e.remove_children()
        elem._e.remove_attr('id', XMLNS)
        elem._e.text = self.simple_lemmatized_edition_form
        return elem
    
    @cached_property
    def simple_lemmatized_edition_form(self) -> str:
        """
        Form for use as text in the simple_lemmatized_edition_element
        """
        return self.normalized_form

    @cached_property
    def normalized_form(self) -> str:
        """
        Returns the normalized form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>.
        Compare @form and @orig_form
        """
        
        if self.representable_cls_inst is None:
            return self._e.text_desc
        if type(self.representable_cls_inst) is type(self):
            raise TypeError(f'Class {type(self)} must implement property `normalized_form`.')
        return self.representable_cls_inst.normalized_form
    
    @cached_property
    def orig_form(self) -> str:
        """
        Returns the original form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>.
        Compare @form and @normalized_form
        """
        non_ancestors = RegTextType.values()

        ancestors_str = ' and '.join([f'not(ancestor::ns:{ancestor})' 
                                 for ancestor in non_ancestors])

        normalized_text = self._e.xpath(f'descendant::text()[{ancestors_str}]')
        return self._e._clean_text(''.join([str(t) for t in normalized_text]))
    
    @property
    def representable_cls_inst(self) -> RepresentableElement | None:
        """
        An instance of a class inheriting from Representable giving 
        behaviours specific to the element in question, e.g. W, G, Expan etc.
        """

        cls = self.elem_classes.get(self._e.localname)
        if cls is None:
            return None
        inst = cls(self._e)
        return inst

    @property
    def type(self) -> str:
        return self._e.tag.name
