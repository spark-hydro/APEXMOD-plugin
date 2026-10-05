


def import_rt3d_salt_dates():
    comp = "NO3 (Nitrate)".replace('(', '').replace(')', '').strip().split()[1].lower()
    # if (
    #     comp != "solute" and
    #     self.dlg.radioButton_rt3d_m.isChecked() and
    #     comp != "nitrate" and
    #     comp != "phosphorus"
    #     ):
    #     post_viii_salt.read_salt_dates(self)
    # if (
    #     (comp == "nitrate" or comp == "phosphorus") and
    #     self.dlg.radioButton_rt3d_m.isChecked()
    #     ):
    #     post_vii_nitrate.read_rt3d_dates(self)
    #     post_vii_nitrate.read_mf_nOflayers(self)
    print(comp)


if __name__ == "__main__":
    # wd = "/Users/seonggyu.park/Documents/projects/kokshila/analysis/koksilah_swatmf/SWAT-MODFLOW"
    wd = "D:/Projects/Watersheds/Koksilah/analysis/koksilah_swatmf/SWAT-MODFLOW"
    # outfd = "d:/Projects/Watersheds/Okavango/Analysis/2nd_cali"
    # get_rech_avg_m_df(wd).to_csv(os.path.join(outfd, 'test.csv'))
    obd_file = "dtw_day.obd.csv"
    startDate = "1/1/2009"
    import_rt3d_salt_dates()